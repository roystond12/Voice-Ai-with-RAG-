import json
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
import config
from sentence_transformers import SentenceTransformer, CrossEncoder
import chromadb
from chromadb.api.models.Collection import Collection

def get_generation_model():
    tokenizer = AutoTokenizer.from_pretrained(config.GENERATION_MODEL)
    model = AutoModelForCausalLM.from_pretrained(config.GENERATION_MODEL)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    return tokenizer,model

def chunk_to_text(chunk: dict) -> str:
    parts = []

    title = chunk.get("title")
    if title:
        parts.append(title)

    description = chunk.get("description")
    if description:
        parts.append(description)

    for key, value in chunk.get("elements", {}).items():
        if value:
            clean_key = key.replace("_", " ").strip()
            parts.append(f"{clean_key}. {value}")

    for table in chunk.get("tables", []):
        markdown = table.get("markdown")
        if markdown:
            parts.append(markdown)

    for caption in chunk.get("images", []):
        if caption:
            parts.append(f"Image description: {caption}")

    return "\n\n".join(parts)

def generate_answer(query: str, chunks: list[dict], tokenizer, model) -> str:
    context = "\n\n".join(chunk_to_text(chunk) for chunk in chunks)
    messages = [
        {"role": "system", "content":config.PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
    ]
    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
    ).to(model.device)

    output_ids = model.generate(
        **inputs,
        max_new_tokens=config.MAX_NEW_TOKENS,
        do_sample=False,
    )
    generated = output_ids[0][inputs["input_ids"].shape[-1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()

def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(config.EMBEDDING_MODEL_ID, trust_remote_code=True)

def get_rerank_model() -> CrossEncoder:
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def get_chroma_client() -> chromadb.HttpClient:
    """Connects to a Chroma *server* (see docker-compose.yml / `chroma run`),
    never an embedded/local-mode client — that would only allow one process
    to hold the store at a time, blocking multi-worker deployment."""
    return chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)


def get_or_create_collection(client: chromadb.HttpClient) -> Collection:
    """Never resets/deletes an existing collection implicitly — a prior bug
    here wiped the vector store on every backend restart. Resets only ever
    happen via an explicit, separate migration/ingestion script."""
    return client.get_or_create_collection(
        name=config.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def get_all_chunks(collection: Collection) -> list[dict]:
    """Every chunk currently indexed in Chroma (the actual source of truth
    for retrieve())."""
    result = collection.get(include=["metadatas"])
    return [json.loads(metadata["chunk_json"]) for metadata in result["metadatas"]]

def retrieve(
    query: str,
    embedding_model: SentenceTransformer,
    re_rank_model: CrossEncoder,
    collection: Collection,
    top_k: int = config.TOP_K,
    rerank_candidates: int = 10,
) -> list[tuple[float, dict]]:
    query_vector = embedding_model.encode(config.PREFIX + query, normalize_embeddings=True).tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=rerank_candidates,
        include=["metadatas"],
    )
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    payloads = [json.loads(metadata["chunk_json"]) for metadata in metadatas]

    pairs = [(query, chunk_to_text(payload)) for payload in payloads]
    if not pairs:
        return []
    rerank_scores = re_rank_model.predict(pairs)

    reranked = sorted(
        zip(rerank_scores, payloads),
        key=lambda pair: pair[0],
        reverse=True,
    )
    return reranked[:top_k]


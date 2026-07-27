import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
import config
from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from qdrant_client.models import Distance,VectorParams

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

def get_qdrant_client(reset: bool = True) -> QdrantClient:
    client = QdrantClient(path=config.QDRANT_PATH)
    if client.collection_exists(config.COLLECTION_NAME):
        existing_dim = client.get_collection(config.COLLECTION_NAME).config.params.vectors.size
        if reset or existing_dim != config.EMBEDDING_DIM:
            client.delete_collection(config.COLLECTION_NAME)
    if not client.collection_exists(config.COLLECTION_NAME):
        client.create_collection(
            collection_name=config.COLLECTION_NAME,
            vectors_config=VectorParams(size=config.EMBEDDING_DIM, distance=Distance.COSINE),
        )
    return client


def get_all_chunks(client: QdrantClient) -> list[dict]:
    """Every chunk currently indexed in Qdrant (the actual source of truth
    for retrieve())."""
    points, _ = client.scroll(
        collection_name=config.COLLECTION_NAME,
        limit=client.count(collection_name=config.COLLECTION_NAME).count,
        with_payload=True,
        with_vectors=False,
    )
    return [point.payload for point in points]

def retrieve(
    query: str,
    embedding_model: SentenceTransformer,
    re_rank_model: CrossEncoder,
    client: QdrantClient,
    top_k: int = config.TOP_K,
    rerank_candidates: int = 10,
) -> list[tuple[float, dict]]:
    query_vector = embedding_model.encode(config.PREFIX + query, normalize_embeddings=True).tolist()
    results = client.query_points(
        collection_name=config.COLLECTION_NAME,
        query=query_vector,
        limit=rerank_candidates,
    )

    pairs = [(query, chunk_to_text(hit.payload)) for hit in results.points]
    if not pairs:
        return []
    rerank_scores = re_rank_model.predict(pairs)

    reranked = sorted(
        zip(rerank_scores, (hit.payload for hit in results.points)),
        key=lambda pair: pair[0],
        reverse=True,
    )
    return reranked[:top_k]


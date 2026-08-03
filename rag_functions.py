import json
import logging
import threading

import torch
from transformers import AutoTokenizer, TextIteratorStreamer
import config
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.api.models.Collection import Collection

import transformers.utils as _tf_utils
if not hasattr(_tf_utils, "is_offline_mode"):
    from huggingface_hub import is_offline_mode as _is_offline_mode
    _tf_utils.is_offline_mode = _is_offline_mode

from optimum.onnxruntime import ORTModelForSequenceClassification, ORTModelForCausalLM

logger = logging.getLogger(__name__)


def get_generation_model():
    """Loads the ONNX-exported generation model + its tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(config.GENERATION_SAVE_DIR)
    model = ORTModelForCausalLM.from_pretrained(config.GENERATION_SAVE_DIR, provider="CPUExecutionProvider")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    return tokenizer, model


def get_streamer(tokenizer: AutoTokenizer, skip_prompt, skip_special_tokens):
    """Builds a token streamer for incremental generation output."""
    return TextIteratorStreamer(tokenizer=tokenizer, skip_prompt=skip_prompt, skip_special_tokens=skip_special_tokens)


def chunk_to_text(chunk: dict) -> str:
    """Renders one retrieved chunk dict into plain text for the LLM/reranker."""
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


def _run_generation(model, generation_kwargs, streamer) -> None:
    """Runs model.generate() in a background thread, always ending the
    streamer so the consumer loop can't hang if generation fails."""
    try:
        model.generate(**generation_kwargs)
    except Exception:
        logger.exception("generation failed")
    finally:
        streamer.end()


def generate_answer(query: str, chunks: list[dict], tokenizer, model):
    """Generator: yields the answer incrementally as the model produces it,
    instead of blocking until the full answer is ready."""
    streamer = get_streamer(tokenizer, True, True)
    context = "\n\n".join(chunk_to_text(chunk) for chunk in chunks)
    messages = [
        {"role": "system", "content": config.PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
    ]
    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
    ).to(model.device)

    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=config.MAX_NEW_TOKENS,
        do_sample=False,
    )

    thread = threading.Thread(target=_run_generation, args=(model, generation_kwargs, streamer), daemon=True)
    thread.start()

    for text in streamer:
        yield text


def get_embedding_model() -> SentenceTransformer:
    """Loads the embedding model used for both indexing and query retrieval."""
    return SentenceTransformer(config.EMBEDDING_MODEL_ID, trust_remote_code=True)


def get_rerank_model():
    """Loads the ONNX-exported reranker model + its tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(config.RERANKED_SAVE_DIR)
    model = ORTModelForSequenceClassification.from_pretrained(config.RERANKED_SAVE_DIR, provider="CPUExecutionProvider")
    return tokenizer, model


def get_chroma_client() -> chromadb.HttpClient:
    """Connects to the Chroma server (see docker-compose.yml / `chroma run`)."""
    return chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)


def get_or_create_collection(client: chromadb.HttpClient) -> Collection:
    """Gets (or creates) the collection without ever resetting existing data."""
    return client.get_or_create_collection(
        name=config.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def get_all_chunks(collection: Collection) -> list[dict]:
    """Every chunk currently indexed in Chroma."""
    result = collection.get(include=["metadatas"])
    return [json.loads(metadata["chunk_json"]) for metadata in result["metadatas"]]


def retrieve(
    query: str,
    embedding_model: SentenceTransformer,
    re_rank_tokenizer,
    re_rank_model,
    collection: Collection,
    top_k: int = config.TOP_K,
    rerank_candidates: int = 4,
) -> list[tuple[float, dict]]:
    """Vector-searches Chroma for candidate chunks, reranks them with the
    cross-encoder, and returns the top_k (score, chunk) pairs."""
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

    queries, passages = zip(*pairs)
    inputs = re_rank_tokenizer(
        list(queries), list(passages), padding=True, truncation=True, return_tensors="pt"
    )
    with torch.no_grad():
        logits = re_rank_model(**inputs).logits
    rerank_scores = logits.squeeze(-1).tolist()

    reranked = sorted(
        zip(rerank_scores, payloads),
        key=lambda pair: pair[0],
        reverse=True,
    )
    return reranked[:top_k]

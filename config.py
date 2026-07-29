import os
import re


PROMPT = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "context below. You are strictly prohibited from answering using anything "
    "outside the context. If the answer to the question is not clearly and "
    "directly contained in the context, you must reply with EXACTLY this and "
    "nothing else: Out of context sorry"
)

GENERATION_MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
EMBEDDING_MODEL_ID = "BAAI/bge-large-en-v1.5"

PREFIX = "use this context for searching as per the relevancy of the query : "

TOP_K = 3

# cross-encoder/ms-marco-MiniLM-L-6-v2 outputs a raw relevance logit (not a
# 0-1 probability); scores at/below 0 mean the pair is judged not relevant.
# Below this, we treat the query as unanswerable from the indexed context and
# skip generation entirely rather than trust the small instruct model to
# self-police off-context questions.
RERANK_SCORE_THRESHOLD = float(os.environ.get("RERANK_SCORE_THRESHOLD", 0.0))
OUT_OF_CONTEXT_MESSAGE = "Out of context sorry"

# Chroma runs as its own server (see docker-compose.yml) so multiple backend
# workers can share one vector store safely, unlike embedded/local-mode clients.
CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", 8100))
CHROMA_COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION_NAME", "vectorDB")

# Legacy local Qdrant store — kept only so scripts/migrate_qdrant_to_chroma.py
# can read old data. Not used by the running app anymore.
QDRANT_PATH = "qdrant_db"
QDRANT_COLLECTION_NAME = "vectorDB"

EMBEDDING_DIM = 1024
# Answers here are meant to be spoken back (TTS), not read as long-form text —
# shorter caps keep both generation time and playback length reasonable.
MAX_NEW_TOKENS = 160

MAX_CONCURRENT_GENERATIONS = int(os.environ.get("MAX_CONCURRENT_GENERATIONS", os.cpu_count() or 2))
QUERY_CACHE_TTL_SECONDS = int(os.environ.get("QUERY_CACHE_TTL_SECONDS", 600))
QUERY_CACHE_MAX_SIZE = int(os.environ.get("QUERY_CACHE_MAX_SIZE", 256))

HEADING_LABELS = {"section_header", "title"}

NUMBERED_HEADING_PATTERN = re.compile(r"^\d{1,2}[.)]\s+\S")
NUMBERED_HEADING_MAX_LEN = 80

ALLOWED_FILE_TYPES = ["image/jpg","image/jpeg","image/png","image/webp","application/pdf","application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

STORAGE_FOLDER = "storage"
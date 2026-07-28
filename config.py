import os

PROMPT = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "context below. If the answer isn't in the context, say you don't know. youre strictly prohibited to answer the question outside of context and within the context if the answer doesnt lies strictly you have to say i dont know"
)

GENERATION_MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
EMBEDDING_MODEL_ID = "BAAI/bge-large-en-v1.5"

PREFIX = "use this context for searching as per the relevancy of the query : "

TOP_K = 3

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
MAX_NEW_TOKENS = 300

MAX_CONCURRENT_GENERATIONS = int(os.environ.get("MAX_CONCURRENT_GENERATIONS", os.cpu_count() or 2))
QUERY_CACHE_TTL_SECONDS = int(os.environ.get("QUERY_CACHE_TTL_SECONDS", 600))
QUERY_CACHE_MAX_SIZE = int(os.environ.get("QUERY_CACHE_MAX_SIZE", 256))
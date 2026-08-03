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

TOP_K = 2

RERANK_SCORE_THRESHOLD = float(os.environ.get("RERANK_SCORE_THRESHOLD", 0.0))
OUT_OF_CONTEXT_MESSAGE = "Out of context sorry"

CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", 8100))
CHROMA_COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION_NAME", "vectorDB")

QDRANT_PATH = "qdrant_db"
QDRANT_COLLECTION_NAME = "vectorDB"

EMBEDDING_DIM = 1024

MAX_NEW_TOKENS = 160

MAX_CONCURRENT_GENERATIONS = int(os.environ.get("MAX_CONCURRENT_GENERATIONS", os.cpu_count() or 2))
QUERY_CACHE_TTL_SECONDS = int(os.environ.get("QUERY_CACHE_TTL_SECONDS", 600))
QUERY_CACHE_MAX_SIZE = int(os.environ.get("QUERY_CACHE_MAX_SIZE", 256))

HEADING_LABELS = {"section_header", "title"}
RERANKED_SAVE_DIR = "onnx_reranker_output"
GENERATION_SAVE_DIR = "onnx_generation_output"

NUMBERED_HEADING_PATTERN = re.compile(r"^\d{1,2}[.)]\s+\S")
NUMBERED_HEADING_MAX_LEN = 80

ALLOWED_FILE_TYPES = ["image/jpg","image/jpeg","image/png","image/webp","application/pdf","application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

STORAGE_FOLDER = "storage"
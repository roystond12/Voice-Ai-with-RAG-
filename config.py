PROMPT = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "context below. If the answer isn't in the context, say you don't know. youre strictly prohibited to answer the question outside of context and within the context if the answer doesnt lies strictly you have to say i dont know"
)

GENERATION_MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
EMBEDDING_MODEL_ID = "BAAI/bge-large-en-v1.5"

PREFIX = "use this context for searching as per the relevancy of the query : "

TOP_K = 3

QDRANT_PATH = "qdrant_db"

COLLECTION_NAME = "vectorDB"

EMBEDDING_DIM = 1024
MAX_NEW_TOKENS = 300
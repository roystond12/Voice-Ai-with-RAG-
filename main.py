from fastapi import FastAPI
import uvicorn
from tts import tts_router
from rag import rag_router, client as qdrant_client

app = FastAPI()

app.include_router(tts_router)
app.include_router(rag_router)

@app.on_event("shutdown")
def close_qdrant_client():
    qdrant_client.close()

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0")
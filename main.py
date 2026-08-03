import logging
import os

import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from tts import tts_router
from stt import stt_router
from rag import rag_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

if not torch.cuda.is_available():
    torch.set_num_threads(os.cpu_count() or 1)

app = FastAPI()

allowed_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:4173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts_router)
app.include_router(stt_router)
app.include_router(rag_router)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0")

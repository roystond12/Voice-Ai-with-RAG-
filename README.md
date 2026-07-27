# Voice AI

A RAG-powered voice assistant: ask a question, it retrieves context from a local Qdrant vector store, generates an answer with a local LLM, and speaks the answer back through a talking-face UI built in Streamlit.

## Components

- **`main.py`** — FastAPI app exposing the backend APIs.
- **`tts.py`** — `POST /api/text_to_speech`: text in, audio bytes out (Deepgram).
- **`rag.py` / `rag_functions.py`** — `GET /api/get_context`: query in, retrieves relevant chunks from Qdrant, reranks them, and generates an answer with a local Hugging Face model.
- **`config.py`** — model names, Qdrant path/collection, prompt, and generation settings.
- **`streamlit_app.py`** — the UI. Sends your query to `/api/get_context`, then speaks the returned answer in-browser (Web Speech API) with word-by-word highlighting and an animated face, no audio-file round trip.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # or install packages listed below
```

Create a `.env` file in the project root:

```
DEEPGRAM_API_KEY=<your deepgram api key>
DEFAULT_MODEL=aura-2-thalia-en
PORT=8081
HOST=0.0.0.0
```

## Running

Start the backend and the UI in two separate terminals:

```bash
# Terminal 1 — FastAPI backend (tts + rag APIs)
python main.py

# Terminal 2 — Streamlit UI
streamlit run streamlit_app.py
```

Then open the Streamlit app (default http://localhost:8501) and type a question in the input box at the bottom.

## Notes

- `qdrant_db/` is the embedded Qdrant storage folder. It's local, file-locked data (only one process can hold it at a time) and is git-ignored — don't copy it between projects while either is running.
- The generation/embedding/rerank models are loaded once at import time in `rag.py`, so backend startup takes a little while.

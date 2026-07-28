# Voice AI

A RAG-powered voice assistant: ask a question by typing or speaking, it
retrieves context from a Chroma vector store, generates an answer with a
local LLM, and speaks the answer back through a talking-face React UI.

## Components

- **`main.py`** — FastAPI app: routers, CORS, `/health`.
- **`tts.py`** — `POST /api/text_to_speech`: text in, high-quality WAV audio
  out (Deepgram Aura, explicit `linear16`/48kHz/wav for quality).
- **`stt.py`** — `POST /api/speech_to_text`: an uploaded audio clip in,
  transcript out (Deepgram STT) — powers the mic/voice-input flow.
- **`rag.py` / `rag_functions.py`** — `GET /api/get_context`: query in
  (JSON body or `?query=` param), retrieves + reranks relevant chunks from
  Chroma, generates an answer with a local Hugging Face model. Includes a
  concurrency guard and a short-TTL answer cache.
- **`config.py`** — model names, Chroma connection settings, prompt,
  generation/concurrency/cache settings.
- **`frontend/`** — the Vite + React UI. See `frontend/README.md`.
- **`scripts/migrate_qdrant_to_chroma.py`** — one-off migration from the
  project's original Qdrant store, if you have old data to bring across.
- **`loadtest/`** — Locust load tests for all three endpoints.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Node.js.

```bash
uv sync
cd frontend && npm install && cd ..
```

Create a `.env` file in the project root:

```
DEEPGRAM_API_KEY=<your deepgram api key>
DEFAULT_MODEL=aura-2-thalia-en
DEFAULT_STT_MODEL=nova-3
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

## Running locally (without Docker)

```bash
# Terminal 1 — Chroma vector store server
uv run chroma run --host 0.0.0.0 --port 8100 --path ./chroma_db

# Terminal 2 — FastAPI backend
uv run python main.py

# Terminal 3 — React UI
cd frontend && npm run dev   # http://localhost:5173
```

Voice input (mic/VAD) has a Vite dev-server-only quirk — see
`frontend/README.md` if the mic button errors under `npm run dev` (typing
questions always works; `npm run build && npm run preview`, and the Docker
setup below, aren't affected).

## Running with Docker

```bash
docker compose up --build
```

Brings up Chroma, the backend (FastAPI), and the frontend (nginx). Scale
backend workers with `BACKEND_WORKERS` (defaults to 2) — safe now that
Chroma runs as its own server rather than an embedded/local-mode client.

> Docker wasn't available in the environment this was built in, so the
> compose file is written to best practice but hasn't been build-verified —
> please validate `docker compose up --build` in your own environment.

## Load testing

```bash
uv run --group dev locust -f loadtest/locustfile.py --host http://localhost:8000
```

See `loadtest/README.md` for measured results on this dev machine and what
it'd actually take to hit higher throughput (more workers, GPU, etc).

## Notes

- `qdrant_db/` / `qdrant_db1/` are leftovers from the project's original
  Qdrant-based vector store, kept only so the migration script can read old
  data if any exists. The running app no longer uses them.
- The generation/embedding/rerank models load once at backend startup, so
  it takes a little while to become ready — wait for `/health` to respond.
- Chat history in the sidebar is in-memory per browser tab only; there's no
  backend persistence for it across sessions.

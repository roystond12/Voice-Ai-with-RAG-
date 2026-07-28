"""
Load tests for the three backend endpoints.

Run:
    uv run --group dev locust -f loadtest/locustfile.py --host http://localhost:8000

Then open http://localhost:8089, set concurrency/spawn-rate, and target
the 20-50 req/s figure from your capacity planning. Read the actual
achieved RPS and p50/p95 latency Locust reports — don't assume the target
is hit; a single-CPU-worker, 360M-param generation path will very likely
plateau below that without the query cache / multiple workers enabled by
the Chroma-servernefmad migration. See loadtest/README.md.
"""
import os
import random

from locust import HttpUser, task, between

SAMPLE_QUERIES = [
    "What is this project about?",
    "How does the retrieval pipeline work?",
    "What model is used for generation?",
    "Summarize the available context.",
    "What can you help me with?",
]

SAMPLE_TEXTS = {
    "short": "Hello, this is a quick test.",
    "medium": "This is a medium length sentence used to exercise the "
              "text to speech endpoint under load, roughly a paragraph long.",
    "long": ("This is a much longer passage intended to simulate a real "
             "generated answer being read back to the user. " * 5),
}

SAMPLE_AUDIO_PATH = os.path.join(os.path.dirname(__file__), "sample_clip.wav")


class RagUser(HttpUser):
    """Hits GET /api/get_context. Repeats a small pool of queries on purpose
    so the backend's TTL query cache gets exercised (cache hits should be
    near-instant; cold queries pay the full retrieval+generation cost)."""

    wait_time = between(1, 3)

    @task
    def get_context(self):
        query = random.choice(SAMPLE_QUERIES)
        with self.client.get(
            "/api/get_context",
            params={"query": query},
            name="/api/get_context",
            catch_response=True,
        ) as res:
            if res.status_code != 200:
                res.failure(f"status={res.status_code} body={res.text[:200]}")


class TitsUser(HttpUser):
    """Hits POST /api/text_to_speech with varied text lengths."""

    wait_time = between(1, 3)

    @task
    def text_to_speech(self):
        text = random.choice(list(SAMPLE_TEXTS.values()))
        with self.client.post(
            "/api/text_to_speech",
            json={"text": text},
            name="/api/text_to_speech",
            catch_response=True,
        ) as res:
            if res.status_code != 200:
                res.failure(f"status={res.status_code} body={res.text[:200]}")


class SttUser(HttpUser):
    """Hits POST /api/speech_to_text with a fixed sample audio clip."""

    wait_time = between(1, 3)

    @task
    def speech_to_text(self):
        with open(SAMPLE_AUDIO_PATH, "rb") as f:
            audio_bytes = f.read()
        with self.client.post(
            "/api/speech_to_text",
            files={"audio": ("clip.wav", audio_bytes, "audio/wav")},
            name="/api/speech_to_text",
            catch_response=True,
        ) as res:
            if res.status_code != 200:
                res.failure(f"status={res.status_code} body={res.text[:200]}")

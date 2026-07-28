# Load testing

```bash
uv run --group dev locust -f loadtest/locustfile.py --host http://localhost:8000
```

Then open http://localhost:8089, set user count / spawn rate, and run against
your target load. For a headless run with a CSV report:

```bash
uv run --group dev locust -f loadtest/locustfile.py --host http://localhost:8000 \
  --headless -u 20 -r 2 -t 60s --csv=results
```

## What we actually measured here

A 5-user, 40s run against this dev machine (single uvicorn worker, no GPU,
`SmolLM2-360M-Instruct` on CPU) produced, with **0 failures**:

| Endpoint | Median | p95 | Max | Notes |
|---|---|---|---|---|
| `GET /api/get_context` | ~2ms | 21-23s | 23s | Near-instant on cache hits; the long tail is cold CPU-bound generation contending for the same cores |
| `POST /api/text_to_speech` | ~2.3s | 14s | 14s | Deepgram round-trip; degrades once concurrent generation requests are also eating CPU |
| `POST /api/speech_to_text` | ~1.4s | 2.4s | 3s | Network-bound to Deepgram, most consistent of the three |

Aggregate throughput across all three endpoints was **under 1 req/s** even at
only 5 concurrent users. This is expected, not a bug: a 360M-parameter causal
LM doing token-by-token generation on CPU is fundamentally slow, and with a
single uvicorn worker every concurrent `/api/get_context` request competes for
the same CPU cores. This is well short of the 20-50 req/s target — closing
that gap requires infrastructure this box doesn't have, not more code:

- **More uvicorn workers** (`--workers N`) — now actually possible since
  Chroma runs as its own server rather than an embedded/local-mode client
  that only tolerates one process.
- **GPU inference** for the generation/embedding/rerank models — the single
  biggest lever; CPU token-by-token decoding is the dominant cost.
- **The query cache already in `rag.py`** helps a lot for repeated questions
  (near-0ms as shown above) but does nothing for the first, unique ask.
- **Horizontal scaling** (multiple backend containers behind a load balancer)
  once each instance doesn't need its own copy of the models in memory — or
  accept the per-replica memory cost if it does.

Re-run this exact command in your actual target environment and read the
real numbers — don't assume the target is met just because the code changed.

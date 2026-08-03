import asyncio
import logging

from cachetools import TTLCache
from fastapi import APIRouter, Request, HTTPException, status
from starlette.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

import config
import rag_functions

logger = logging.getLogger(__name__)

rag_router = APIRouter()
embedding_model = rag_functions.get_embedding_model()
re_rank_tokenizer, re_rank_model = rag_functions.get_rerank_model()
client = rag_functions.get_chroma_client()
collection = rag_functions.get_or_create_collection(client)
tokenizer, gen_model = rag_functions.get_generation_model()

generation_semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_GENERATIONS)
answer_cache: TTLCache = TTLCache(maxsize=config.QUERY_CACHE_MAX_SIZE, ttl=config.QUERY_CACHE_TTL_SECONDS)
_DONE = object()


def _retrieve_chunks(query: str) -> list[dict] | None:
    """Blocking retrieval + rerank, meant to run in a worker thread. Returns
    None if the query is judged out of context."""
    results = rag_functions.retrieve(query, embedding_model, re_rank_tokenizer, re_rank_model, collection)
    if not results or results[0][0] <= config.RERANK_SCORE_THRESHOLD:
        return None
    return [chunk for _, chunk in results]


async def _stream_answer(query: str, cache_key: str):
    """Streams the answer to the client as it's generated."""
    async with generation_semaphore:
        try:
            chunks = await run_in_threadpool(_retrieve_chunks, query)
        except Exception as e:
            logger.error("retrieval failed: %s", e)
            yield "Sorry, something went wrong while looking that up."
            return

        if chunks is None:
            answer_cache[cache_key] = config.OUT_OF_CONTEXT_MESSAGE
            yield config.OUT_OF_CONTEXT_MESSAGE
            return

        collected = []
        token_gen = rag_functions.generate_answer(query, chunks, tokenizer, gen_model)
        try:
            while True:
                token = await run_in_threadpool(next, token_gen, _DONE)
                if token is _DONE:
                    break
                collected.append(token)
                yield token
        except Exception as e:
            logger.error("generation failed: %s", e)
            if not collected:
                yield "Sorry, something went wrong while generating an answer."
            return

        answer_cache[cache_key] = "".join(collected)


@rag_router.get("/api/get_context")
async def get_context(request: Request):
    """
    Input -> Query (str), either as a JSON body {"query": "<query>"} or as a
        "query" query-string parameter (browsers can't send a body on a GET
        request, so the query-string form exists for the web frontend;
        existing JSON-body callers keep working unchanged).
    Output -> Answer from the LLM, streamed as plain-text chunks as they're
        generated, so the client can start rendering/speaking before the
        full answer is ready — instead of one buffered JSON response.
    """
    query = request.query_params.get("query", "").strip()

    if not query:
        if request.headers.get("content-type", "") != "application/json":
            logger.error("please provide json body or a query param")
            raise HTTPException(
                detail="Provide a 'query' query-string param or a JSON body {\"query\": ...}",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
            )
        body = await request.json()
        query = body.get("query", "").strip()

    if not query:
        logger.error("please provide the query params properly")
        raise HTTPException(
            detail="please provide the query params properly",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    cache_key = query.lower()
    cached = answer_cache.get(cache_key)
    if cached is not None:
        async def cached_stream():
            yield cached
        return StreamingResponse(cached_stream(), media_type="text/plain")

    return StreamingResponse(_stream_answer(query, cache_key), media_type="text/plain")

import asyncio
import logging

from cachetools import TTLCache
from fastapi import APIRouter, Request, HTTPException, status
from starlette.concurrency import run_in_threadpool

import config
import rag_functions

logger = logging.getLogger(__name__)

rag_router = APIRouter()
embedding_model = rag_functions.get_embedding_model()
re_rank_model = rag_functions.get_rerank_model()
client = rag_functions.get_chroma_client()
collection = rag_functions.get_or_create_collection(client)
tokenizer, gen_model = rag_functions.get_generation_model()

# Bounds how many requests can be doing CPU-bound retrieval/generation at
# once, so a burst of concurrent requests queues instead of thrashing/OOMing
# this box, rather than each thread fighting the others for the same CPU/RAM.
generation_semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_GENERATIONS)

# Repeated questions (common in demos/load tests) skip retrieval+generation
# entirely for QUERY_CACHE_TTL_SECONDS.
answer_cache: TTLCache = TTLCache(maxsize=config.QUERY_CACHE_MAX_SIZE, ttl=config.QUERY_CACHE_TTL_SECONDS)


def _answer_query(query: str) -> str:
    """Blocking retrieval + generation, meant to run in a worker thread."""
    results = rag_functions.retrieve(query, embedding_model, re_rank_model, collection)
    chunks = [chunk for score, chunk in results]
    return rag_functions.generate_answer(query, chunks, tokenizer, gen_model)


@rag_router.get("/api/get_context")
async def get_context(request: Request):
    """
    Input -> Query (str), either as a JSON body {"query": "<query>"} or as a
        "query" query-string parameter (browsers can't send a body on a GET
        request, so the query-string form exists for the web frontend;
        existing JSON-body callers keep working unchanged).
    Output -> Answer from llm (str)
    """
    try:
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
            return cached

        async with generation_semaphore:
            answer = await run_in_threadpool(_answer_query, query)

        answer_cache[cache_key] = answer
        return answer

    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate an answer",
        )

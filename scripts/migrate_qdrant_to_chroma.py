"""
One-off migration: copies every point (vector + payload) from the legacy
local Qdrant store (config.QDRANT_PATH) into the new Chroma server
(config.CHROMA_HOST/CHROMA_PORT/CHROMA_COLLECTION_NAME).

Run once, manually, whenever there's old Qdrant data to bring across:
    uv run --group dev python scripts/migrate_qdrant_to_chroma.py

Requires the `qdrant-client` dev dependency (kept only for this script) and
a reachable Chroma server (see docker-compose.yml, or `uv run chroma run`).
"""
import json
import sys

from qdrant_client import QdrantClient

import config
import rag_functions


def main() -> None:
    qdrant = QdrantClient(path=config.QDRANT_PATH)
    if not qdrant.collection_exists(config.QDRANT_COLLECTION_NAME):
        print(f"No Qdrant collection '{config.QDRANT_COLLECTION_NAME}' found at {config.QDRANT_PATH}. Nothing to migrate.")
        sys.exit(0)

    total = qdrant.count(collection_name=config.QDRANT_COLLECTION_NAME).count
    if total == 0:
        print("Qdrant collection is empty. Nothing to migrate.")
        sys.exit(0)

    points, _ = qdrant.scroll(
        collection_name=config.QDRANT_COLLECTION_NAME,
        limit=total,
        with_payload=True,
        with_vectors=True,
    )

    chroma_client = rag_functions.get_chroma_client()
    collection = rag_functions.get_or_create_collection(chroma_client)

    ids = [str(point.id) for point in points]
    embeddings = [point.vector for point in points]
    documents = [rag_functions.chunk_to_text(point.payload) for point in points]
    metadatas = [{"chunk_json": json.dumps(point.payload)} for point in points]

    collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    print(f"Migrated {len(ids)} points from Qdrant ({config.QDRANT_PATH}) to Chroma collection '{config.CHROMA_COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()

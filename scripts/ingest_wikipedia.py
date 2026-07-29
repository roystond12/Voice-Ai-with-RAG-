"""
One-off ingestion: pulls plaintext Wikipedia articles and indexes them into
the Chroma collection, one chunk per section, using the same chunk schema
(`{title, description, elements, tables, images}`) that `rag_functions.py`
already knows how to render and retrieve.

Run once, manually:
    uv run python scripts/ingest_wikipedia.py
"""
import json
import re
import sys

import requests

import config
import rag_functions

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

# Core Michael Jackson topics — enough breadth for bio / discography /
# career / death questions without pulling in the entire back catalogue.
PAGE_TITLES = [
    "Michael Jackson",
    "Thriller (album)",
    "Bad (album)",
    "Off the Wall",
    "Death of Michael Jackson",
    "The Jackson 5",
]

# These sections are just link/citation lists, not answerable content.
SKIP_SECTIONS = {
    "references",
    "external links",
    "see also",
    "further reading",
    "notes",
    "bibliography",
    "sources",
}

SECTION_HEADING_RE = re.compile(r"^(={2,6})\s*(.+?)\s*\1$", re.MULTILINE)


def fetch_extract(title: str) -> str:
    resp = requests.get(
        WIKI_API_URL,
        params={
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "explaintext": 1,
            "titles": title,
        },
        headers={"User-Agent": "voice-ai-ingest/1.0"},
        timeout=30,
    )
    resp.raise_for_status()
    pages = resp.json().get("query", {}).get("pages", {})
    for page in pages.values():
        if "extract" in page:
            return page["extract"]
    return ""


def split_into_chunks(page_title: str, extract: str) -> list[dict]:
    """Split a plaintext Wikipedia extract into one chunk per top-level
    section, using the article title as the intro chunk's title."""
    chunks = []
    matches = list(SECTION_HEADING_RE.finditer(extract))

    intro = extract[: matches[0].start()].strip() if matches else extract.strip()
    if intro:
        chunks.append({"title": page_title, "description": intro, "elements": {}, "tables": [], "images": []})

    for i, match in enumerate(matches):
        heading = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(extract)
        body = extract[start:end].strip()
        if not body or heading.lower() in SKIP_SECTIONS:
            continue
        chunks.append(
            {
                "title": f"{page_title} — {heading}",
                "description": body,
                "elements": {},
                "tables": [],
                "images": [],
            }
        )

    return chunks


def main() -> None:
    all_chunks: list[dict] = []
    for title in PAGE_TITLES:
        print(f"Fetching '{title}'...")
        extract = fetch_extract(title)
        if not extract:
            print(f"  no extract found for '{title}', skipping.")
            continue
        chunks = split_into_chunks(title, extract)
        print(f"  -> {len(chunks)} chunks")
        all_chunks.extend(chunks)

    if not all_chunks:
        print("Nothing fetched, aborting.")
        sys.exit(1)

    print(f"\nEmbedding {len(all_chunks)} chunks...")
    embedding_model = rag_functions.get_embedding_model()
    texts = [rag_functions.chunk_to_text(chunk) for chunk in all_chunks]
    # config.PREFIX is a query-side search instruction (see retrieve()) — it
    # only gets prepended to queries at retrieval time, not to documents.
    embeddings = embedding_model.encode(texts, normalize_embeddings=True).tolist()

    client = rag_functions.get_chroma_client()
    collection = rag_functions.get_or_create_collection(client)

    ids = [f"wiki-{i}" for i in range(len(all_chunks))]
    metadatas = [{"chunk_json": json.dumps(chunk)} for chunk in all_chunks]

    collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    print(f"Indexed {len(all_chunks)} chunks into Chroma collection '{config.CHROMA_COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()

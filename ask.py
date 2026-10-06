#!/usr/bin/env python3
"""Join the local index and the pinned tables to the prepperoni tag.

Does not import survivalRAG. Reads the chroma directory that project already built.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
MODEL = os.environ.get("PREPPER_MODEL", "prepperoni")
CHROMA = os.environ.get(
    "PREPPER_CHROMA",
    str(Path.home() / "projects/survivalRAG/data/chroma"),
)
COLLECTION = "survivalrag"
ROOT = Path(__file__).resolve().parent
TABLES = ROOT / "corpus" / "PINNED_TABLES.md"

DOSE_WORDS = (
    "bleach",
    "water",
    "drink",
    "iodide",
    "ki ",
    " ki",
    "dose",
    "mr/h",
    "mR",
    "radiation",
    "fallout",
    "7-10",
    "amoxicillin",
    "antibiotic",
)


def post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        OLLAMA + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())


def embed(text: str) -> list[float]:
    data = post("/api/embed", {"model": "nomic-embed-text", "input": "search_query: " + text})
    return data["embeddings"][0]


def is_dose(question: str) -> bool:
    q = question.lower()
    return any(w.lower() in q for w in DOSE_WORDS)


def best_chunk(question: str) -> str:
    import chromadb

    client = chromadb.PersistentClient(path=CHROMA)
    col = client.get_collection(COLLECTION)
    result = col.query(query_embeddings=[embed(question)], n_results=1)
    docs = result.get("documents") or [[]]
    metas = result.get("metadatas") or [[]]
    if not docs or not docs[0]:
        return ""
    meta = metas[0][0] or {}
    source = meta.get("source_document") or meta.get("source_title") or "unknown"
    page = meta.get("page_number")
    section = meta.get("section_header") or ""
    locator = f"{source}, p.{page}" if page else source
    if section:
        locator = f"{locator}, {section}"
    return f"Retrieved passage ({locator}):\n{docs[0][0]}"


def build_prompt(question: str) -> str:
    if is_dose(question):
        tables = TABLES.read_text() if TABLES.exists() else "PINNED_TABLES.md missing"
        return (
            "Pinned tables follow. Use them. Do not recall a number from training.\n\n"
            + tables
            + "\n\nQuestion: "
            + question
        )
    chunk = best_chunk(question)
    if not chunk:
        return question + "\n\nNo page was retrieved for this question."
    return chunk + "\n\nQuestion: " + question


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print('usage: python ask.py "beach shade shelter"', file=sys.stderr)
        sys.exit(2)
    prompt = build_prompt(question)
    data = post("/api/generate", {"model": MODEL, "prompt": prompt, "stream": False})
    print(data.get("response", "").strip())


if __name__ == "__main__":
    main()

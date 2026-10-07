#!/usr/bin/env python3
"""Join the local index and the pinned tables to the prepperoni tag.

Does not import survivalRAG. Reads the chroma directory that project already built.
Procedure questions get the top 3 chunks. Dose questions get the pinned tables only.
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
N_FETCH = 12
N_CHUNKS = 3
STEP_WORDS = ("cut ", "foil", "instructions", "template", "to scale", "soup", "thread", "leaves")

DOSE_WORDS = (
    "bleach",
    "drinking water",
    "safe to drink",
    "iodide",
    "ki ",
    " ki",
    "dose rate",
    "mr/h",
    "mR",
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


def locator(meta: dict) -> str:
    source = meta.get("source_document") or meta.get("source_title") or "unknown"
    page = meta.get("page_number")
    section = meta.get("section_header") or ""
    loc = f"{source}, p.{page}" if page else source
    if section and section not in loc:
        loc = f"{loc}, {section}"
    return loc


def best_chunks(question: str) -> str:
    import chromadb

    client = chromadb.PersistentClient(path=CHROMA)
    col = client.get_collection(COLLECTION)
    pairs = []
    q = question.lower()
    if "kearny" in q or "kfm" in q or "fallout meter" in q:
        got = col.get(where={"source_document": "ORNL-5040"}, where_document={"$contains": "foil"})
        for doc, meta in zip(got.get("documents") or [], got.get("metadatas") or []):
            if doc:
                pairs.append((doc, meta or {}))
    if len(pairs) < N_CHUNKS:
        result = col.query(query_embeddings=[embed(question)], n_results=N_FETCH)
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        for i, doc in enumerate(docs):
            if doc:
                pairs.append((doc, metas[i] if i < len(metas) and metas[i] else {}))
    ranked = []
    for doc, meta in pairs:
        score = sum(1 for w in STEP_WORDS if w in doc.lower())
        ranked.append((score, doc, meta))
    ranked.sort(key=lambda item: -item[0])
    blocks = []
    seen = set()
    for score, doc, meta in ranked:
        loc = locator(meta)
        if loc in seen:
            continue
        seen.add(loc)
        blocks.append(f"Passage {len(blocks) + 1} ({loc}):\n{doc}")
        print(f"using {loc} score={score}", file=sys.stderr)
        if len(blocks) == N_CHUNKS:
            break
    return "\n\n".join(blocks)


def build_prompt(question: str) -> str:
    if is_dose(question):
        tables = TABLES.read_text() if TABLES.exists() else "PINNED_TABLES.md missing"
        return (
            "Pinned tables follow. Use them. Do not recall a number from training.\n\n"
            + tables
            + "\n\nQuestion: "
            + question
        )
    chunks = best_chunks(question)
    if not chunks:
        return question + "\n\nNo page was retrieved for this question."
    return (
        "Retrieved passages follow. Use the passage that contains the requested steps. "
        "Cite that passage's report and page. Do not use a passage that only points at the steps. "
        "If none of the passages contain the steps, say no page retrieved.\n\n"
        + chunks
        + "\n\nQuestion: "
        + question
    )


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print('usage: python ask.py "how do I build a Kearny fallout meter"', file=sys.stderr)
        sys.exit(2)
    data = post("/api/generate", {"model": MODEL, "prompt": build_prompt(question), "stream": False})
    print(data.get("response", "").strip())


if __name__ == "__main__":
    main()

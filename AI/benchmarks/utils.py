from __future__ import annotations

import json
import time
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .. import core
from ..document_ingestion.ingestion import DocumentIngestionService


def chunk_text(text: str, max_chars: int = 900, overlap: int = 150) -> list[str]:
    text = " ".join((text or "").split())
    if not text:
        return []
    chunks: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        j = min(n, i + max_chars)
        cut = text.rfind(". ", i, j)
        if cut == -1 or cut < i + max_chars * 0.5:
            cut = j
        else:
            cut = cut + 1
        chunk = text[i:cut].strip()
        if chunk:
            chunks.append(chunk)
        i = max(i + 1, cut - overlap)
    return chunks


def bootstrap_sample_data(r) -> int:
    """Ingest (upsert) AI/sample_data into Redis and return inserted chunk count."""
    sample_dir = Path(__file__).resolve().parents[1] / "sample_data"
    svc = DocumentIngestionService()
    inserted = 0

    files = sorted([p for p in sample_dir.iterdir() if p.is_file()])
    for fp in files:
        raw = fp.read_bytes()
        h = hashlib.sha256(raw).hexdigest()[:12]
        stable_doc_id = f"sample_{fp.stem}_{h}"
        doc = svc.ingest(str(fp))
        chunks = chunk_text(doc.text)
        if not chunks:
            continue
        vecs = core.embed_texts(chunks)
        for idx, (t, v) in enumerate(zip(chunks, vecs)):
            key = core.make_key(stable_doc_id, str(idx))
            core.upsert_chunk(r=r, key=key, text=t, embedding=v)
            inserted += 1
    return inserted


def run_one(r, question: str, k: int = 6) -> dict[str, Any]:
    qv = core.embed_texts([question])[0]
    hits = core.knn_search(r, qv, k=k)

    prompt = core.build_rag_prompt(question, hits)
    answer = core.ollama_generate(prompt)

    return {
        "question": question,
        "answer": answer,
        "retrieval": [
            {
                "key": h.get("key"),
                "score": float(h.get("score", 0.0)),
                "content": h.get(core._SCHEMA_TEXT_FIELD, ""),
            }
            for h in hits
        ],
    }


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

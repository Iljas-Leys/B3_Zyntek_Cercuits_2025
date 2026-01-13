from __future__ import annotations

"""Benchmark helpers.

Fixes the previous mismatch where benchmarks called `core.upsert_chunk(...)` without metadata.

These helpers are used by:
  - AI/benchmarks/run_baseline.py
  - AI/benchmarks/run_eval.py
"""

import json
from pathlib import Path
from typing import Any

from .. import core
from ..chunking import chunk_document, stable_doc_id_from_bytes
from ..document_ingestion.ingestion import DocumentIngestionService


def bootstrap_sample_data(r) -> int:
    """Ingest (upsert) AI/sample_data into Redis and return inserted chunk count.

    This is intentionally idempotent:
      - we use a stable doc_id derived from bytes
      - keys are deterministic: <prefix>:<doc_id>:<chunk_id>
      - repeated calls simply overwrite the same hashes
    """
    sample_dir = Path(__file__).resolve().parents[1] / "sample_data"
    svc = DocumentIngestionService()
    inserted = 0

    for fp in sorted([p for p in sample_dir.iterdir() if p.is_file()]):
        raw = fp.read_bytes()
        stable_doc_id = stable_doc_id_from_bytes(fp.name, raw, prefix="sample")

        # Parse (also stores to ./storage, but that's fine for local dev)
        doc = svc.ingest(str(fp))

        chunks = chunk_document(
            doc_id=stable_doc_id,
            text=doc.text,
            source=str(fp.name),
            title=fp.stem,
            file_type=fp.suffix.lower(),
            strategy="auto",
        )
        if not chunks:
            continue

        vecs = core.embed_texts([c.text for c in chunks])
        for c, v in zip(chunks, vecs):
            key = core.make_key(stable_doc_id, c.chunk_id)
            core.upsert_chunk(
                r=r,
                key=key,
                text=c.text,
                embedding=v,
                metadata={
                    "doc_id": c.doc_id,
                    "chunk_id": c.chunk_id,
                    "source": c.source,
                    "title": c.title,
                    "file_type": c.file_type,
                    "start_char": c.start_char,
                    "end_char": c.end_char,
                },
            )
            inserted += 1

    return inserted


def run_one(r, question: str, k: int = 6) -> dict[str, Any]:
    """Run one benchmark question through the *grounded* RAG pipeline."""
    answer, hits = core.rag_answer(r, question, k=k)

    return {
        "question": question,
        "answer": answer,
        "retrieval": [
            {
                "key": h.get("key"),
                "score": float(h.get("score")) if isinstance(h.get("score"), (int, float)) else None,
                "content": h.get(core._SCHEMA_TEXT_FIELD, ""),
            }
            for h in hits
        ],
    }


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

# AI/retrieval_real.py
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from . import core
from .document_ingestion.ingestion import DocumentIngestionService


def _chunk_text(text: str, max_chars: int = 900, overlap: int = 150) -> list[str]:
    text = " ".join((text or "").split())
    if not text:
        return []
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        j = min(n, i + max_chars)
        # try to cut on a boundary
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


def _bootstrap_sample_data(r) -> int:
    # Ingest AI/sample_data into Redis if index empty
    sample_dir = Path(__file__).resolve().parent / "sample_data"
    svc = DocumentIngestionService()
    inserted = 0

    files = sorted([p for p in sample_dir.iterdir() if p.is_file()])
    for fp in files:
        raw = fp.read_bytes()
        h = hashlib.sha256(raw).hexdigest()[:12]
        stable_doc_id = f"sample_{fp.stem}_{h}"
        doc = svc.ingest(str(fp))
        chunks = _chunk_text(doc.text)
        if not chunks:
            continue
        vecs = core.embed_texts(chunks)
        for idx, (t, v) in enumerate(zip(chunks, vecs)):
            key = core.make_key(stable_doc_id, str(idx))
            core.upsert_chunk(r=r, key=key, text=t, embedding=v)
            inserted += 1
    return inserted


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--bootstrap-sample-data", action="store_true")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / "redisSchema.yaml"

    r = core.get_redis()
    core.ensure_index(str(schema_path))

    if args.bootstrap_sample_data:
        if core.redis_index_doc_count(r, core.REDIS_INDEX_NAME) == 0:
            inserted = _bootstrap_sample_data(r)
            print(f"[BOOTSTRAP] Inserted {inserted} chunks from AI/sample_data")

    qv = core.embed_texts([args.query])[0]
    hits = core.knn_search(r, qv, k=args.k)

    if not hits:
        print("[WARN] No hits. (Is your index empty or key prefix incorrect?)")
        return 2

    for h in hits:
        score = h.get("score")
        txt = h.get(core._SCHEMA_TEXT_FIELD, "")
        print(f"- score={score:.6f} key={h.get('key')}")
        print(txt[:700])
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

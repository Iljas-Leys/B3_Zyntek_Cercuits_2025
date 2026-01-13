# AI/retrieval_real.py
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import core
from .chunking import chunk_document, stable_doc_id_from_bytes
from .document_ingestion.ingestion import DocumentIngestionService


def _bootstrap_sample_data(r) -> int:
    # Ingest AI/sample_data into Redis if index empty
    sample_dir = Path(__file__).resolve().parent / "sample_data"
    svc = DocumentIngestionService()
    inserted = 0

    files = sorted([p for p in sample_dir.iterdir() if p.is_file()])
    for fp in files:
        raw = fp.read_bytes()
        stable_doc_id = stable_doc_id_from_bytes(fp.name, raw, prefix="sample")
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


def _bootstrap_storage_extracted_text(r) -> int:
    """Upsert chunks from repo-root storage/extracted_text (sample data already parsed)."""
    repo_root = Path(__file__).resolve().parents[1]
    extracted_dir = repo_root / "storage" / "extracted_text"
    meta_dir = repo_root / "storage" / "metadata"

    if not extracted_dir.exists():
        return 0

    inserted = 0
    for txt_path in sorted(extracted_dir.glob("*.txt")):
        raw = txt_path.read_bytes()
        text = raw.decode("utf-8", errors="replace")

        meta = {}
        meta_path = meta_dir / f"{txt_path.stem}.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                meta = {}

        # ✅ Use stable doc_id here too (optional, but correct)
        doc_id = stable_doc_id_from_bytes(txt_path.name, raw, prefix="storage")

        title = meta.get("filename") or txt_path.stem
        file_type = meta.get("file_type") or ""
        source = str(txt_path.relative_to(repo_root))

        chunks = chunk_document(
            doc_id=doc_id,
            text=text,
            source=source,
            title=title,
            file_type=file_type,
            strategy="auto",
        )
        if not chunks:
            continue
        vecs = core.embed_texts([c.text for c in chunks])
        for c, v in zip(chunks, vecs):
            key = core.make_key(doc_id, c.chunk_id)
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--raw", action="store_true", help="Show raw KNN hits (no filtering/diversity)")
    ap.add_argument("--answer", action="store_true", help="Also run grounded RAG answer generation")
    ap.add_argument("--bootstrap-sample-data", action="store_true")
    ap.add_argument("--bootstrap-storage-data", action="store_true")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / "redisSchema.yaml"

    r = core.get_redis()
    core.ensure_index(str(schema_path))

    if args.bootstrap_sample_data:
        if core.redis_index_doc_count(r, core.REDIS_INDEX_NAME) == 0:
            inserted = _bootstrap_sample_data(r)
            print(f"[BOOTSTRAP] Inserted {inserted} chunks from AI/sample_data")

    if args.bootstrap_storage_data:
        if core.redis_index_doc_count(r, core.REDIS_INDEX_NAME) == 0:
            inserted = _bootstrap_storage_extracted_text(r)
            print(f"[BOOTSTRAP] Inserted {inserted} chunks from storage/extracted_text")

    if args.answer:
        answer, hits = core.rag_answer(r, args.query, k=args.k)
        print("[ANSWER]", answer)
        print()
    else:
        if args.raw:
            qv = core.embed_texts([args.query])[0]
            hits = core.knn_search(r, qv, k=args.k)
        else:
            hits = core.retrieve_chunks(r, args.query, k=args.k)

    if not hits:
        print("[WARN] No hits. (Is your index empty or key prefix incorrect?)")
        return 2

    for h in hits:
        score = h.get("score")
        key = h.get("key")
        txt = h.get(core._SCHEMA_TEXT_FIELD, "")

        if isinstance(score, (int, float)):
            print(f"- score={score:.6f} key={key}")
        else:
            print(f"- score=? key={key}")

        print(str(txt)[:700])
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

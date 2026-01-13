"""AI/index_storage.py

SCRUM-142 / SCRUM-145

Index documents already extracted into repo-root `storage/extracted_text` into Redis.

Usage examples (from repo root):
  python -m AI.index_storage --recreate-index
  python -m AI.index_storage --strategy auto
  python -m AI.index_storage --strategy semantic
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from . import core
from .chunking import chunk_document


def _content_hash(text: str) -> str:
    # Normalize whitespace so trivial formatting differences don't create new IDs
    normalized = " ".join(text.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def index_storage(*, strategy: str = "auto") -> int:
    repo_root = Path(__file__).resolve().parents[1]
    extracted_dir = repo_root / "storage" / "extracted_text"
    meta_dir = repo_root / "storage" / "metadata"

    if not extracted_dir.exists():
        print(f"[WARN] Missing folder: {extracted_dir}")
        return 0

    r = core.get_redis()
    core.ensure_index(str(repo_root / "redisSchema.yaml"))

    inserted = 0
    seen_hashes: set[str] = set()

    for txt_path in sorted(extracted_dir.glob("*.txt")):
        text = txt_path.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            continue

        meta = {}
        meta_path = meta_dir / f"{txt_path.stem}.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                meta = {}

        # Deterministic ID: same content -> same doc_id (fixes duplicates permanently)
        ch = _content_hash(text)

        # Skip duplicate content within a single indexing run
        if ch in seen_hashes:
            continue
        seen_hashes.add(ch)

        # If metadata has a stable document_id you trust, you can incorporate it,
        # but NEVER use timestamped stems as identity.
        base_id = meta.get("document_id")
        if base_id and isinstance(base_id, str) and base_id.strip():
            doc_id = f"{base_id.strip()}_{ch}"
        else:
            doc_id = f"storage_{ch}"

        title = meta.get("filename") or txt_path.stem
        file_type = meta.get("file_type") or ""
        source = str(txt_path.relative_to(repo_root))

        chunks = chunk_document(
            doc_id=doc_id,
            text=text,
            source=source,
            title=title,
            file_type=file_type,
            strategy=strategy,  # type: ignore[arg-type]
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
    ap.add_argument("--strategy", default="auto", choices=["auto", "semantic", "recursive", "both"])
    ap.add_argument("--recreate-index", action="store_true", help="Drop + recreate RediSearch index")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / "redisSchema.yaml"

    if args.recreate_index:
        core.create_index_from_yaml(str(schema_path), drop_existing=True)
        print(f"[OK] Recreated index: {core.REDIS_INDEX_NAME}")

    inserted = index_storage(strategy=args.strategy)
    print(f"[OK] Inserted {inserted} chunks from storage/extracted_text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

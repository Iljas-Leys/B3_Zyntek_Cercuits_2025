from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

from .utils import bootstrap_sample_data, run_one, save_json
from .. import core


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default=None, help="Path to questions.json (defaults to AI/benchmarks/questions.json)")
    ap.add_argument("--out", default=None, help="Output path (defaults to AI/benchmarks/baseline.json)")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--reset-index", action="store_true", help="DROPINDEX+DD then recreate index before running")
    ap.add_argument("--bootstrap-sample-data", action="store_true", help="Ingest AI/sample_data if index is empty (recommended)")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    schema_path = repo_root / "redisSchema.yaml"

    q_path = Path(args.questions) if args.questions else (Path(__file__).resolve().parent / "questions.json")
    out_path = Path(args.out) if args.out else (Path(__file__).resolve().parent / "baseline.json")

    r = core.get_redis()
    if args.reset_index:
        core.create_index_from_yaml(str(schema_path), drop_existing=True)

    core.ensure_index(str(schema_path))

    inserted = 0
    if args.bootstrap_sample_data:
        inserted = bootstrap_sample_data(r)

    questions = json.loads(q_path.read_text(encoding="utf-8"))
    q_list = questions.get("questions", [])

    results = []
    for q in q_list:
        item = run_one(r, q["question"], k=args.k)
        item["id"] = q["id"]
        results.append(item)

    payload = {
        "type": "baseline",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "index": core.REDIS_INDEX_NAME,
        "k": args.k,
        "bootstrapped_chunks": inserted,
        "questions_version": questions.get("version"),
        "results": results,
    }

    save_json(out_path, payload)

    stamped = out_path.with_name("baseline_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".json")
    save_json(stamped, payload)

    print(f"[OK] Baseline saved to: {out_path}")
    print(f"[OK] Snapshot saved to: {stamped}")
    if inserted:
        print(f"[OK] Bootstrapped {inserted} chunks from AI/sample_data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

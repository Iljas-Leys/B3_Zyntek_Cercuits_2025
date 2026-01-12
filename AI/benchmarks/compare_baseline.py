from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

from .. import core


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return float(np.dot(a, b) / denom)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--min_answer_sim", type=float, default=0.80)
    ap.add_argument("--min_retrieval_overlap", type=float, default=0.20)
    args = ap.parse_args()

    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    cand = json.loads(Path(args.candidate).read_text(encoding="utf-8"))

    base_map = {r["id"]: r for r in base.get("results", [])}
    cand_map = {r["id"]: r for r in cand.get("results", [])}

    ids = sorted(set(base_map.keys()) & set(cand_map.keys()))
    if not ids:
        print("[FAIL] No overlapping question IDs between baseline and candidate.")
        return 3

    base_answers = [base_map[i].get("answer","") for i in ids]
    cand_answers = [cand_map[i].get("answer","") for i in ids]

    # Embed answers and compute cosine similarity per question
    emb_base = core.embed_texts(base_answers)
    emb_cand = core.embed_texts(cand_answers)

    sims = []
    overlaps = []
    for idx, qid in enumerate(ids):
        sim = _cosine(emb_base[idx], emb_cand[idx])
        sims.append(sim)

        base_keys = {x.get("key") for x in base_map[qid].get("retrieval", []) if x.get("key")}
        cand_keys = {x.get("key") for x in cand_map[qid].get("retrieval", []) if x.get("key")}
        if not base_keys and not cand_keys:
            ov = 1.0
        else:
            ov = len(base_keys & cand_keys) / float(len(base_keys | cand_keys) or 1)
        overlaps.append(ov)

        print(f"{qid}: answer_sim={sim:.3f}  retrieval_overlap={ov:.3f}")

    avg_sim = float(np.mean(sims))
    avg_ov = float(np.mean(overlaps))

    print()
    print(f"AVG answer_sim={avg_sim:.3f} (min={args.min_answer_sim})")
    print(f"AVG retrieval_overlap={avg_ov:.3f} (min={args.min_retrieval_overlap})")

    passed = (avg_sim >= args.min_answer_sim) and (avg_ov >= args.min_retrieval_overlap)
    if passed:
        print("[PASS] Candidate is consistent with baseline (within thresholds).")
        return 0
    else:
        print("[FAIL] Candidate deviates from baseline beyond thresholds.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Mechanically reconcile four Wikipedia Stage A editorial branches.

No mathematical re-review. Preserve all accepted formulations and all holds.
Validate exact identity/coverage against frozen Stage A source queues and
produce immutable next-stage candidate and hold worklists.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

REL = Path("work/wikipedia-stage-a/20261103")
EXPECTED = 1121


def read_jsonl(path):
    return [json.loads(row) for row in path.read_text(encoding="utf-8").splitlines()
            if row.strip()]


def dump_jsonl(path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n"
                            for item in items), encoding="utf-8")


def check_text_list(value):
    return isinstance(value, list) and all(isinstance(s, str) and s.strip() for s in value)


def run(stage_a_root: Path, worker_root: Path, out: Path):
    expected_by_id = {}
    index = {}
    lane_expected = {}
    for lane in range(1, 5):
        files = [stage_a_root / f"worker-{lane}" / f
                 for f in ("needs_interpretation.jsonl", "mechanical_suggestions.jsonl")]
        rows = [item for f in files for item in read_jsonl(f)]
        lane_ids = set()
        for row in rows:
            cid, url = row["candidate_id"], row["url"]
            if cid in expected_by_id or cid in lane_ids:
                raise ValueError("Repeated candidate ID in Stage A source: " + cid)
            if not cid.startswith("candidate.wikipedia.") or urlsplit(url).netloc != "en.wikipedia.org":
                raise ValueError("Invalid source candidate identity: " + cid)
            if cid != "candidate.wikipedia." + hashlib.sha256(url.encode()).hexdigest()[:20]:
                raise ValueError("Source ID no longer matches URL: " + cid)
            if row.get("worker") != lane:
                raise ValueError(f"Source lane mismatch: {cid}")
            if not isinstance(row.get("input_index"), int):
                raise ValueError("Missing source input position: " + cid)
            index[row["input_index"]] = cid
            lane_ids.add(cid)
            expected_by_id[cid] = row
        lane_expected[lane] = lane_ids
    if len(expected_by_id) != EXPECTED or set(index) != set(range(EXPECTED)):
        raise ValueError("Frozen Stage A sources are not 1121 continuous input positions")

    result_by_id = {}
    counts_by_lane = {}
    for lane in range(1, 5):
        path = worker_root / f"worker-{lane}" / REL / f"worker-{lane}" / "editorial_decisions.jsonl"
        rows = read_jsonl(path)
        ids = [r.get("candidate_id") for r in rows]
        if len(ids) != len(set(ids)) or set(ids) != lane_expected[lane]:
            missing, extra = lane_expected[lane] - set(ids), set(ids) - lane_expected[lane]
            raise ValueError(f"Worker {lane}: duplicate/missing/extra IDs: {len(missing)} missing, {len(extra)} extra")
        c = Counter()
        for r in rows:
            cid = r["candidate_id"]
            source = expected_by_id[cid]
            if r.get("url") != source["url"] or r.get("title") != source["title"]:
                raise ValueError("Worker changed source identity: " + cid)
            if r.get("source_statement_excerpt") != source.get("source_statement_excerpt"):
                raise ValueError("Worker changed the source statement excerpt: " + cid)
            status = r.get("status")
            if status not in ("standalone_prepared", "held_for_source_clarity"):
                raise ValueError("Unrecognized editorial status for " + cid)
            if not check_text_list(r.get("hypotheses")) or not check_text_list(r.get("conclusions")):
                raise ValueError("Malformed search-side text lists for " + cid)
            if not isinstance(r.get("editorial_note"), str):
                raise ValueError("Missing editorial note for " + cid)
            if status == "standalone_prepared":
                if (not isinstance(r.get("statement"), str) or not r["statement"].strip() or
                        not r["conclusions"]):
                    raise ValueError("Incomplete prepared theorem: " + cid)
            elif r.get("statement") is not None or r["hypotheses"] or r["conclusions"]:
                raise ValueError("Held candidate should not pretend to contain a complete theorem: " + cid)
            new = dict(r)
            new["input_index"] = source["input_index"]
            new["stage_a_worker"] = lane
            new["editorial_status"] = status
            new["editorial_review"] = "standalone_statement_prepared_not_proof_checked" if (
                status == "standalone_prepared") else "held_for_source_clarity"
            new["source_excerpt"] = source.get("source_excerpt")
            new["source_section"] = r.get("source_section") or source.get("source_section")
            new["source_fidelity"] = source.get("source_fidelity")
            result_by_id[cid] = new
            c[status] += 1
        counts_by_lane[str(lane)] = dict(sorted(c.items()))

    if len(result_by_id) != EXPECTED:
        raise ValueError("Missing globally reconciled decisions")
    ordered = [result_by_id[index[i]] for i in range(EXPECTED)]
    prepared = [r for r in ordered if r["status"] == "standalone_prepared"]
    holds = [r for r in ordered if r["status"] == "held_for_source_clarity"]
    if len(prepared) != 984 or len(holds) != 137:
        raise ValueError("Unexpected editorial results changed; inspect worker revisions")

    out.mkdir(parents=True, exist_ok=True)
    dump_jsonl(out / "decisions.jsonl", ordered)
    dump_jsonl(out / "prepared_statements.jsonl", prepared)
    dump_jsonl(out / "held_statements.jsonl", holds)
    (out / "prepared_urls.txt").write_text("\n".join(r["url"] for r in prepared) + "\n", encoding="utf-8")
    report = {
        "schema": "maththm.wikipedia-stage-a-reconciliation.v1",
        "sources": "four independently completed Stage A worker branches",
        "original_unmatched_urls": EXPECTED,
        "reconciled_decisions": len(ordered),
        "prepared_statements": len(prepared),
        "held_for_source_clarity": len(holds),
        "worker_counts": counts_by_lane,
        "duplicate_candidate_ids": 0,
        "missing_candidate_ids": 0,
        "foreign_candidate_ids": 0,
        "proofs_screened": 0,
        "published": 0,
        "next_stage": "cursory proof accessibility/completion screening; no proof correctness audit",
    }
    (out / "REPORT.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--worker-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    run(a.sources, a.worker_root, a.output)


if __name__ == "__main__":
    main()

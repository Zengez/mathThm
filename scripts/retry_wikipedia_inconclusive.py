#!/usr/bin/env python3
"""One controlled reattempt of ONLY the 224 previously inconclusive Wikipedia pages.

No scheduled scans, no theorem re-review. Wikipedia's API returned HTTP 429 in
the first pass; throttle sequentially and stop early if repeated 429s recur.
Previously screened 706 and 54 original nonpasses are never retried or modified.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import time

from scripts.screen_wikipedia_proof_sections import screen_one

ORIGINAL = Path("work/wikipedia-proof-screen/20261104/decisions.jsonl")
PREPARED = Path("work/wikipedia-existing-match/20261104/unmatched_prepared.jsonl")
OUTPUT = Path("work/wikipedia-proof-screen/20261104/one-time-retry")
DATE = "2026-11-04"
PASS = "appears_to_contain_proof"
NO_PROOF = "no_visible_proof"
INCONCLUSIVE = "inconclusive"
SKIPPED = "not_retried_rate_limit"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def dump_jsonl(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows),
                    encoding="utf-8")


def rate_limited(result: dict) -> bool:
    if result.get("status") != INCONCLUSIVE:
        return False
    messages = result.get("fetch_notes") or []
    return any(("HTTP Error 429" in str(s) or "Too Many Requests" in str(s))
               for s in messages)


def prepared_record(candidate: dict, decision: dict) -> dict:
    """Reapply the exact original structural-screen acquisition field shape."""
    c = dict(candidate)
    c["proof_screening"] = decision
    c["proofs"] = [{
        "url": decision["proof_url"],
        "locator": decision["proof_heading"],
        "screening": "cursory_screened",
        "accessed_on": DATE,
        "screening_scope": decision["screening_scope"],
        "screening_basis": decision["reason"],
    }]
    c["acquisition"] = {
        "status": "cursory_screened",
        "batch_id": "wikipedia-structural-proof-retry-20261104",
        "collected_on": DATE,
    }
    return c


def run(original: Path, prepared: Path, output: Path, delay: float,
        stop_after_429: int, screener=screen_one, sleeper=time.sleep) -> dict:
    first = read_jsonl(original)
    prepared_rows = read_jsonl(prepared)
    if len(first) != 984 or len(prepared_rows) != 984:
        raise ValueError("Expected exactly 984 original decisions and 984 prepared candidates")
    if any(a["candidate_id"] != b["candidate_id"] or a["url"] != b["url"]
           for a, b in zip(first, prepared_rows)):
        raise ValueError("Source records do not match by stable ID and URL")
    if len({r["candidate_id"] for r in first}) != 984:
        raise ValueError("Duplicate original candidate IDs")
    original_counts = Counter(r["status"] for r in first)
    if dict(original_counts) != {PASS: 706, NO_PROOF: 54, INCONCLUSIVE: 224}:
        raise ValueError("Unexpected original screening counts: " + repr(original_counts))

    pending = [(r, p) for r, p in zip(first, prepared_rows) if r["status"] == INCONCLUSIVE]
    decisions, newly_passed, newly_no_proof, still_pending = [], [], [], []
    rate_limit_streak = 0
    stopped_early = False

    for k, (old, source) in enumerate(pending, 1):
        if rate_limit_streak >= stop_after_429:
            stopped_early = True
            new = {
                "candidate_id": source["candidate_id"],
                "url": source["url"],
                "title": source["title"],
                "input_index": source["input_index"],
                "status": SKIPPED,
                "reason": "Stopped after repeated HTTP 429; defer until later",
                "proof_url": old.get("proof_url"),
                "inspection_date": DATE,
            }
            attempted = False
        else:
            new = screener(source)
            attempted = True
        if (new["candidate_id"] != old["candidate_id"] or
            new["url"] != old["url"] or
            new["status"] not in (PASS, NO_PROOF, INCONCLUSIVE, SKIPPED)):
            raise ValueError("Retry changed identity or returned unrecognized status")
        row = dict(new)
        row["attempted"] = attempted
        row["original_status"] = old["status"]
        row["original_reason"] = old["reason"]
        row["original_fetch_notes"] = old.get("fetch_notes")
        decisions.append(row)

        if new["status"] == PASS:
            if not new.get("proof_url"):
                raise ValueError("Passed screening has no real proof-section URL")
            newly_passed.append(prepared_record(source, new))
        elif new["status"] == NO_PROOF:
            r = dict(source)
            r["retry_proof_screening"] = new
            newly_no_proof.append(r)
        else:
            r = dict(source)
            r["initial_proof_screening"] = old
            r["retry_proof_screening"] = new
            still_pending.append(r)

        # Stop if blocked rather than making hundreds of further Wikipedia calls.
        if attempted:
            rate_limit_streak = rate_limit_streak + 1 if rate_limited(new) else 0
            if delay and k < len(pending) and rate_limit_streak < stop_after_429:
                sleeper(delay)
        if k % 20 == 0 or rate_limit_streak >= stop_after_429 and attempted:
            print(f"Retry {k}/224: "
                  f"{dict(Counter(r['status'] for r in decisions))}",flush=True)

    if len(decisions) != 224 or len({r["candidate_id"] for r in decisions}) != 224:
        raise ValueError("Failed to account for all 224 retry candidates")
    if len(newly_passed) + len(newly_no_proof) + len(still_pending) != 224:
        raise ValueError("Combined retry queues do not partition the 224 candidates")
    summary = Counter(x["status"] for x in decisions)
    report = {
        "schema": "maththm.wikipedia-proof-presence-one-time-retry.v1",
        "date": DATE,
        "original_total": 984,
        "original_screened": 706,
        "original_no_visible_proof": 54,
        "original_inconclusive": 224,
        "retry_attempted": sum(x["attempted"] for x in decisions),
        "retry_skipped_due_to_rate_limit": summary[SKIPPED],
        "retry_proof_looking_content_found": summary[PASS],
        "retry_no_visible_proof": summary[NO_PROOF],
        "retry_still_inconclusive_attempted": summary[INCONCLUSIVE],
        "updated_total_screened": 706 + summary[PASS],
        "updated_total_no_visible_proof": 54 + summary[NO_PROOF],
        "updated_total_inconclusive_or_deferred": summary[INCONCLUSIVE] + summary[SKIPPED],
        "rate_limit_stop_triggered": stopped_early,
        "retry_reasons": dict(sorted(Counter(x["reason"] for x in decisions).items())),
        "previous_source_clarity_holds_untouched": 137,
        "proof_validity_checked": False,
        "proof_completeness_checked": False,
        "theorems_published": 0,
        "scheduled": False,
        "followup": "Leave unresolved cases for a future manual retry, not a recurring job",
    }
    assert (report["updated_total_screened"] +
            report["updated_total_no_visible_proof"] +
            report["updated_total_inconclusive_or_deferred"] == 984)
    output.mkdir(parents=True, exist_ok=True)
    dump_jsonl(output / "retry_decisions.jsonl", decisions)
    dump_jsonl(output / "newly_screened_candidates.jsonl", newly_passed)
    dump_jsonl(output / "newly_no_visible_proof.jsonl", newly_no_proof)
    dump_jsonl(output / "still_inconclusive_or_deferred.jsonl", still_pending)
    (output / "newly_screened_urls.txt").write_text(
        "".join(x["url"]+"\n" for x in newly_passed), encoding="utf-8")
    (output / "still_pending_urls.txt").write_text(
        "".join(x["url"]+"\n" for x in still_pending), encoding="utf-8")
    (output / "REPORT.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)+"\n",
        encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False),flush=True)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original", type=Path, default=ORIGINAL)
    p.add_argument("--prepared", type=Path, default=PREPARED)
    p.add_argument("--output", type=Path, default=OUTPUT)
    p.add_argument("--delay", type=float, default=1.5)
    p.add_argument("--stop-after-429", type=int, default=4)
    a = p.parse_args()
    if a.delay < 1.0 or a.stop_after_429 < 2:
        p.error("Require >=1 second between cases and >=2 consecutive 429s")
    run(a.original, a.prepared, a.output, a.delay, a.stop_after_429)


if __name__ == "__main__":
    main()

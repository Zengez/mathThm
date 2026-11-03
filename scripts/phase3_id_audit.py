#!/usr/bin/env python3
"""Audit the four frozen Phase 3 worker lanes against pinned Stage B inputs.

Read-only: never grants Phase 2 approval, imports Pass 3 results, or publishes.
Run from repo root with full Git history available:
    python scripts/phase3_id_audit.py --report /tmp/phase3-id-audit.json
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
BASE = "c57a162275ef35a7fe61e87f709627fd98ede4de"
PINNED_SOURCE = "a04446e57ec1fbc252a871afcec7752fb2807b14"
POSITIVE = "source_equivalence_approved_pending_materialization"
CONTENT = ("statement", "hypotheses", "conclusions", "logical_form")
PROMOTION_FLAGS = ("phase2_authoritative_registered", "phase3_eligible",
                   "official_pass3_admissible", "phase2_validated", "published")
MAX_EXAMPLES = 35


def git(*args):
    result = subprocess.run(("git", *args), cwd=ROOT, check=True,
                            capture_output=True, text=True)
    return result.stdout.strip()


def jsonlines(path):
    p = ROOT / path
    if not p.is_file():
        raise FileNotFoundError(path)
    records = []
    for index, line in enumerate(p.read_text(encoding="utf8").splitlines(), 1):
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{index}: {exc}") from exc
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()
    alloc = json.loads((ROOT / "work/phase3-parallel/ALLOCATION.json").read_text())
    issues = Counter()
    examples = {}
    worker_results = []
    global_inputs, global_proposals, global_reviews = {}, {}, {}
    all_stageb = set()
    total_held = 0
    checked_files = 0

    def fail(category, detail):
        issues[category] += 1
        sample = examples.setdefault(category, [])
        if len(sample) < MAX_EXAMPLES:
            sample.append(str(detail))

    if alloc.get("stage_b_approved_preliminary") != 3866:
        fail("allocation_expected_count", alloc.get("stage_b_approved_preliminary"))
    if alloc.get("pinned_source_revision") != PINNED_SOURCE:
        fail("allocation_source_revision", alloc.get("pinned_source_revision"))
    if git("rev-parse", BASE) != BASE:
        fail("base_commit", BASE)
    if git("merge-base", "--is-ancestor", BASE, "HEAD") != "":
        pass

    for n in range(1, 5):
        path = f"work/phase3-parallel/worker-{n}/PENDING.json"
        frozen = json.loads(git("show", f"{BASE}:{path}"))
        current = json.loads((ROOT / path).read_text(encoding="utf8"))
        allocated = next(x for x in alloc["workers"] if x["worker"] == n)
        expected = allocated["expected_positive_ids"]
        all_batches = frozen["pending"]
        worker_input, worker_props, worker_reviews = set(), set(), set()
        outcomes = Counter()
        held_worker = 0
        sections = 0

        if frozen["pending"] == []:
            fail("frozen_queue_missing", n)
        if current.get("pending") != []:
            fail("worker_queue_not_empty", n)
        if len(all_batches) != allocated["initial_batches"]:
            fail("batch_count", f"worker {n}: {len(all_batches)}")
        if frozen.get("expected_positive_ids") != expected:
            fail("frozen_expected_positive_ids", n)

        for batch in all_batches:
            for section in batch["sections"]:
                sections += 1
                srcfile = section["file"]
                chap = section["chapter"]
                line = section["section_start_line"]
                sha = section["blob_sha"]
                name = f"{chap}/section-{line}.jsonl"
                propfile = f"work/phase3-parallel/worker-{n}/phase2_proposals/{name}"
                prooffile = f"work/phase3-parallel/worker-{n}/proof_reviews/{name}"
                if srcfile in all_stageb:
                    fail("duplicate_input_section", srcfile)
                all_stageb.add(srcfile)
                try:
                    if git("hash-object", srcfile) != sha:
                        fail("stage_b_blob_sha_mismatch", srcfile)
                    source = jsonlines(srcfile)
                    proposals = jsonlines(propfile)
                    reviews = jsonlines(prooffile)
                except (FileNotFoundError, ValueError, subprocess.CalledProcessError) as exc:
                    fail("unreadable_section", str(exc))
                    continue
                checked_files += 1
                positives = [r for r in source if r.get("decision") == POSITIVE]
                held_worker += len(source) - len(positives)
                p_ids = [r.get("candidate_id") for r in positives]
                q_ids = [r.get("candidate_id") for r in proposals]
                r_ids = [r.get("candidate_id") for r in reviews]

                if len(set(p_ids)) != len(p_ids):
                    fail("duplicate_positive_ids_in_section", srcfile)
                if len(set(q_ids)) != len(q_ids):
                    fail("duplicate_proposal_ids_in_section", propfile)
                if len(set(r_ids)) != len(r_ids):
                    fail("duplicate_review_ids_in_section", prooffile)
                if p_ids != q_ids or p_ids != r_ids:
                    fail("section_id_order_or_coverage", f"{srcfile}: input={p_ids}, proposals={q_ids}, reviews={r_ids}")
                if set(p_ids) != set(q_ids):
                    fail("section_proposal_set_mismatch", srcfile)
                if set(p_ids) != set(r_ids):
                    fail("section_proof_set_mismatch", srcfile)

                p_by_id = {r.get("candidate_id"): r for r in proposals}
                r_by_id = {r.get("candidate_id"): r for r in reviews}
                for stage_b in source:
                    cid = stage_b.get("candidate_id")
                    if stage_b.get("decision") != POSITIVE:
                        if cid in p_by_id or cid in r_by_id:
                            fail("held_id_leaked", f"{srcfile}: {cid}")
                        continue
                    if cid in global_inputs:
                        fail("duplicate_stageb_id_global", cid)
                    global_inputs[cid] = srcfile
                    worker_input.add(cid)

                    for key, expected_value in (
                        ("source_revision", PINNED_SOURCE),
                        ("source_file", f"{chap}.tex"),
                        ("section_start_line", line),
                        ("source_first_review", True),
                        ("proof_reviewed", False),
                    ):
                        if stage_b.get(key) != expected_value:
                            fail("stage_b_metadata", f"{cid}: {key}")
                    if not isinstance(stage_b.get("source_line"), int):
                        fail("stage_b_missing_source_line", cid)
                    if not stage_b.get("review_note"):
                        fail("stage_b_missing_review_note", cid)
                    for key in CONTENT:
                        if not stage_b.get(key):
                            fail("stage_b_missing_content", f"{cid}: {key}")

                    pair = ((p_by_id.get(cid), "proposal", propfile),
                            (r_by_id.get(cid), "proof", prooffile))
                    for obj, kind, artifact in pair:
                        if obj is None:
                            continue
                        target = global_proposals if kind == "proposal" else global_reviews
                        local = worker_props if kind == "proposal" else worker_reviews
                        if cid in target:
                            fail(f"duplicate_{kind}_id_global", cid)
                        target[cid] = artifact
                        local.add(cid)
                        if obj.get("source_revision") not in (None, PINNED_SOURCE):
                            fail(f"{kind}_source_revision_mismatch", cid)
                        for flag in PROMOTION_FLAGS:
                            if obj.get(flag) is True:
                                fail("premature_authoritative_promotion", f"{kind}: {cid}: {flag}")
                        digestpath = obj.get("stage_b_result_file") or obj.get("stage_b_path")
                        if kind == "proof":
                            digestpath = digestpath or obj.get("stage_b_reviewed_content_identity", {}).get("stage_b_file")
                        if digestpath is not None and digestpath != srcfile:
                            fail(f"{kind}_stage_b_path_mismatch", cid)
                        digest = (obj.get("stage_b_result_blob_sha") or
                                  obj.get("stage_b_blob_sha") or
                                  obj.get("stage_b_git_blob_sha"))
                        if kind == "proof":
                            digest = digest or obj.get("stage_b_reviewed_content_identity", {}).get("stage_b_blob_sha")
                        if digest is not None and digest != sha:
                            fail(f"{kind}_stage_b_blob_mismatch", cid)

                        if kind == "proposal":
                            identity = obj.get("source_identity", obj)
                            for key in ("source_revision", "source_file", "source_line", "original_source_statement_tex"):
                                if key in identity and identity[key] != stage_b.get(key):
                                    fail("proposal_original_source_mismatch", f"{cid}: {key}")
                            if obj.get("source_statement_sha256") is not None:
                                source_digest = hashlib.sha256(stage_b["original_source_statement_tex"].encode("utf8")).hexdigest()
                                if obj["source_statement_sha256"] != source_digest:
                                    fail("proposal_source_digest_mismatch", cid)
                            prepared = (obj.get("stage_b_reviewed_content") or obj.get("reviewed_content") or obj)
                        else:
                            prepared = obj.get("stage_b_reviewed_content")
                            outcome = obj.get("outcome")
                            outcomes[str(outcome)] += 1
                            if not outcome:
                                fail("proof_missing_outcome", cid)
                            if obj.get("scan_completed") is not True and outcome == "plausible":
                                fail("plausible_without_completed_scan", cid)
                            if not str(obj.get("reason") or "").strip():
                                fail("proof_missing_reason", cid)
                            checked = obj.get("proof_checked_on")
                            try:
                                date.fromisoformat(checked)
                            except (TypeError, ValueError):
                                fail("proof_invalid_review_date", cid)
                            if obj.get("proof_screening_confidence") not in (None, "brief_scan_only"):
                                fail("proof_confidence_unexpected", cid)
                            if outcome == "plausible":
                                start = obj.get("proof_start_line")
                                end = obj.get("proof_end_line")
                                if not isinstance(start, int) or not isinstance(end, int) or start > end:
                                    fail("plausible_missing_proof_range", cid)
                        if prepared is not None:
                            if prepared.get("candidate_id", cid) != cid:
                                fail(f"{kind}_prepared_id_mismatch", cid)
                            if prepared.get("source_revision", PINNED_SOURCE) != PINNED_SOURCE:
                                fail(f"{kind}_prepared_revision_mismatch", cid)
                            for key in CONTENT:
                                if key in prepared and prepared[key] != stage_b.get(key):
                                    fail("final_content_changed_since_stage_b", f"{kind}: {cid}: {key}")
                    if cid not in p_by_id:
                        fail("missing_proposal_id", cid)
                    if cid not in r_by_id:
                        fail("missing_review_id", cid)

        if sections != allocated["source_section_files"]:
            fail("worker_section_count", f"{n}: {sections}")
        if len(worker_input) != expected:
            fail("worker_positive_count", f"{n}: {len(worker_input)} / {expected}")
        if worker_input != worker_props:
            fail("worker_proposal_id_set", f"{n}: {len(worker_input-worker_props)} missing, {len(worker_props-worker_input)} extra")
        if worker_input != worker_reviews:
            fail("worker_proof_id_set", f"{n}: {len(worker_input-worker_reviews)} missing, {len(worker_reviews-worker_input)} extra")
        worker_results.append({
            "worker": n, "frozen_batches": len(all_batches), "sections": sections,
            "positive_ids": len(worker_input), "proposal_ids": len(worker_props),
            "proof_review_ids": len(worker_reviews), "held_rows_excluded": held_worker,
            "proof_outcomes": dict(sorted(outcomes.items()))
        })
        total_held += held_worker

    expected_total = alloc["stage_b_approved_preliminary"]
    for category, actual in (
        ("total_positive_id_count", len(global_inputs)),
        ("total_proposal_id_count", len(global_proposals)),
        ("total_review_id_count", len(global_reviews)),
    ):
        if actual != expected_total:
            fail(category, f"{actual} != {expected_total}")
    if total_held != alloc["stage_b_held_excluded"]:
        fail("total_held_count", f"{total_held} != {alloc['stage_b_held_excluded']}")
    if checked_files != alloc["section_files"]:
        fail("total_section_files", f"{checked_files} != {alloc['section_files']}")
    if set(global_inputs) != set(global_proposals):
        fail("global_proposal_set_difference", f"missing={len(set(global_inputs)-set(global_proposals))}, extra={len(set(global_proposals)-set(global_inputs))}")
    if set(global_inputs) != set(global_reviews):
        fail("global_review_set_difference", f"missing={len(set(global_inputs)-set(global_reviews))}, extra={len(set(global_reviews)-set(global_inputs))}")
    report = {
        "schema": "maththm.phase3.id-audit.v1",
        "integration_commit": git("rev-parse", "HEAD"),
        "base_commit": BASE,
        "source_revision": PINNED_SOURCE,
        "result": "PASS" if not issues else "FAIL",
        "frozen_positive_ids": expected_total,
        "positive_ids_verified": len(global_inputs),
        "proposal_ids_verified": len(global_proposals),
        "proof_review_ids_verified": len(global_reviews),
        "held_rows_excluded": total_held,
        "sections_verified": checked_files,
        "workers": worker_results,
        "outcomes": dict(sorted(sum((Counter(r["proof_outcomes"]) for r in worker_results), Counter()).items())),
        "issue_counts": dict(sorted(issues.items())),
        "issue_examples": examples,
        "limitations": [
            "Proves exact frozen Stage B / worker ID and content linkage, not mathematical correctness.",
            "Proof ranges are inspected as metadata; this audit does not reread full original Stacks proofs.",
            "Phase 2 authoritative approval and official Phase 3 admission are separate gates."
        ]
    }
    out = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(out)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(out, encoding="utf8")
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())

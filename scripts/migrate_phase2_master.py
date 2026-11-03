#!/usr/bin/env python3
"""One-time, fail-closed Phase 2 record migration to a permanent common schema.

The output is MATERIALIZED JSONL, never a runtime compatibility layer.
The original worker review is embedded as an archival JSON snapshot so that
the source worker files may later be retired without losing audit evidence.
This command does not register approvals or publish any theorem.

Usage:
  python scripts/migrate_phase2_master.py --write
  python scripts/migrate_phase2_master.py --validate
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work/phase2-final-parallel"
MASTER = ROOT / "data/maththm_master.jsonl"
REPORT = ROOT / "work/phase2-canonical-migration/REPORT.json"
REGISTRY = ROOT / "harvest/PHASE2_AUTHORITATIVE_REGISTRY.json"
BASE = "7c9e0b3168f592a460ab014559b8305d3ab42301"
SOURCE_REV = "a04446e57ec1fbc252a871afcec7752fb2807b14"
SCHEMA = "maththm.master.v1"
CONTENT_FIELDS = ("candidate_id", "source_revision", "statement", "hypotheses",
                  "conclusions", "logical_form", "structured_cases", "equivalence_sides")
FORM_FIELDS = CONTENT_FIELDS[2:]
EXPECTED_WORKER = (766, 765, 765, 765)
EXPECTED_SECTIONS = (224, 264, 242, 264)
EXPECTED_BATCHES = (31, 33, 30, 32)


def json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git_blob(path):
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def read_jsonl(path):
    with (ROOT / path).open(encoding="utf-8") as handle:
        return [json.loads(s) for s in handle if s.strip()]


def frozen_queue(worker):
    path = f"work/phase2-final-parallel/worker-{worker}/PENDING.json"
    proc = subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=ROOT,
                          text=True, capture_output=True, check=True)
    return json.loads(proc.stdout)


def content_digest(cid, rev, form):
    payload = {"candidate_id": cid, "source_revision": rev}
    payload.update({k: form.get(k) for k in FORM_FIELDS})
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def archived_snapshot(kind, path, row, row_number):
    snapshot = json_text(row)
    return {"kind": kind, "path": str(path), "row_number": row_number,
            "content_sha256": sha256(snapshot), "original_record_json": snapshot}


def choose(obj, *names):
    for name in names:
        value = obj.get(name)
        if value is not None:
            return value
    return None


def canonical(cid, row, *, origin, worker=None, batch_id=None, section=None,
              phase3=None, provenance=None, snapshots=None):
    provenance = provenance or {}
    original = row.get("original_source_statement_tex")
    rev = row.get("source_revision")
    source_file = row.get("source_file")
    source_line = row.get("source_line")
    form_raw = row.get("final_content")
    if not isinstance(form_raw, dict):
        form_raw = row
    form = {key: form_raw.get(key) for key in FORM_FIELDS}
    decision = row.get("decision") if origin == "final_worker" else "source_equivalence_approved"
    registered = origin == "historical_authoritative"
    flags = []
    if rev != SOURCE_REV:
        flags.append("source_revision_mismatch")
    if not isinstance(cid, str) or not cid:
        flags.append("missing_candidate_id")
    if not isinstance(original, str) or not original.strip():
        flags.append("missing_original_source_statement")
    source_hash = row.get("source_statement_sha256")
    computed_source_hash = sha256(original) if isinstance(original, str) else None
    if source_hash is not None and source_hash != computed_source_hash:
        flags.append("original_source_digest_mismatch")
    if source_hash is None:
        source_hash = computed_source_hash

    if decision not in ("source_equivalence_approved", "source_equivalence_held"):
        flags.append("invalid_phase2_decision")
    approved = decision == "source_equivalence_approved"
    approved_hash = row.get("approved_content_sha256")
    if approved:
        if any(not form.get(k) for k in ("statement", "hypotheses", "conclusions", "logical_form")):
            flags.append("incomplete_approved_formulation")
        if approved_hash != content_digest(cid, rev, form):
            flags.append("approved_formulation_digest_mismatch")
    elif approved_hash is not None:
        flags.append("held_record_has_approval_digest")
    # Worker 3 included the formulation both at the top and under final_content.
    if isinstance(row.get("final_content"), dict):
        for k in FORM_FIELDS:
            if k in row and row[k] != form[k]:
                flags.append("nested_and_top_level_formulation_disagree:" + k)

    ref = row.get("referenced_immutable_inputs") or {}
    if not isinstance(ref, dict):
        ref = {}
        flags.append("invalid_immutable_input_structure")
    merged = {**row, **ref, **{k: v for k, v in provenance.items() if v is not None}}
    stage_a = choose(merged, "stage_a_artifact", "reconstruction_artifact")
    stage_a_sha = choose(merged, "stage_a_blob_sha", "stage_a_artifact_git_blob_sha")
    stage_b_path = choose(merged, "stage_b_file", "stage_b_result_file", "stage_b_path")
    stage_b_sha = choose(merged, "stage_b_blob_sha", "stage_b_result_blob_sha", "stage_b_git_blob_sha")
    p3_path = choose(merged, "phase3_review_file")
    p3_sha = choose(merged, "phase3_review_blob_sha")
    proposal_path = choose(merged, "phase2_proposal_file")
    proposal_sha = choose(merged, "phase2_proposal_blob_sha")

    stage_b_reviewer = row.get("prior_stage_b_reviewer")
    stage_a_reviewer = choose(row, "prior_stage_a_reviewer", "reconstruction_reviewer")
    independent = row.get("independent_validation")
    if not isinstance(independent, dict):
        independent = {}
    reviewer = row.get("reviewer") or choose(independent, "reviewer", "independent_validator")
    reviewer = reviewer or row.get("mathematical_approval_origin")
    if origin == "final_worker":
        if not reviewer or row.get("source_first_review") is not True:
            flags.append("missing_source_first_reviewer")
        if row.get("proof_reviewed") is not False:
            flags.append("phase2_proof_review_inconsistent")
        if not stage_b_reviewer:
            flags.append("missing_stage_b_reviewer")
        if stage_b_reviewer == reviewer:
            flags.append("phase2_reviewer_not_independent_of_stage_b")
    if registered and (row.get("phase2_validated") is not True or row.get("phase3_eligible") is not True):
        flags.append("historical_authority_flags_inconsistent")
    if approved and not str(row.get("semantic_review_note") or "").strip():
        flags.append("missing_semantic_review_note")
    if phase3 and phase3.get("outcome") != "plausible":
        flags.append("phase3_not_plausible")
    if origin == "final_worker" and not phase3:
        flags.append("missing_phase3_proof_screen")
    if phase3 and phase3.get("stage_b_reviewed_content_sha256_unregistered") not in (None, approved_hash):
        flags.append("phase3_reviewed_content_digest_mismatch")
    source_url = row.get("source_url")
    if not source_url and source_file and isinstance(source_line, int):
        source_url = (f"https://github.com/stacks/stacks-project/blob/"
                      f"{SOURCE_REV}/{source_file}#L{source_line}")

    return {
        "schema": SCHEMA,
        "candidate_id": cid,
        "source": {
            "revision": rev, "file": source_file, "line": source_line,
            "label": row.get("source_label"), "url": source_url,
            "original_statement_tex": original,
            "original_statement_sha256": source_hash,
        },
        "formulation": {
            **form, "approved_content_sha256": approved_hash if approved else None,
        },
        "phase2": {
            "decision": decision, "authoritative_registered": registered,
            "source_first_review": row.get("source_first_review") if not registered
                else choose(independent, "source_first_review"),
            "proof_reviewed": False,
            "reviewer": reviewer,
            "reviewed_on": choose(row, "mathematical_review_date", "review_date", "materialization_date"),
            "prior_stage_a_reviewer": stage_a_reviewer,
            "prior_stage_b_reviewer": stage_b_reviewer,
            "semantic_review_note": row.get("semantic_review_note"),
            "hold_classification": choose(row, "hold_classification", "hold_type", "correction_classification"),
            "hold_reason": row.get("hold_reason"),
            "proposed_correction": row.get("proposed_correction"),
            "duplicate_review_status": row.get("duplicate_review_status"),
            "context_evidence": row.get("context_evidence"),
        },
        "phase3": {
            "outcome": phase3.get("outcome") if phase3 else None,
            "scan_completed": phase3.get("scan_completed") if phase3 else None,
            "reason": phase3.get("reason") if phase3 else None,
            "screening_confidence": phase3.get("proof_screening_confidence") if phase3 else None,
            "proof_checked_on": phase3.get("proof_checked_on") if phase3 else None,
            "proof_file": phase3.get("proof_file") if phase3 else None,
            "proof_start_line": phase3.get("proof_start_line") if phase3 else None,
            "proof_end_line": phase3.get("proof_end_line") if phase3 else None,
            "proof_locator": phase3.get("proof_locator") if phase3 else None,
            "proof_url": phase3.get("proof_url") if phase3 else None,
            "mathematical_audit": phase3.get("mathematical_audit") if phase3 else "not_audited",
        },
        "provenance": {
            "origin": origin, "worker": worker, "batch_id": batch_id,
            "section_start_line": section,
            "stage_a_artifact": stage_a, "stage_a_blob_sha": stage_a_sha,
            "stage_b_file": stage_b_path, "stage_b_blob_sha": stage_b_sha,
            "phase3_review_file": p3_path, "phase3_review_blob_sha": p3_sha,
            "phase2_proposal_file": proposal_path, "phase2_proposal_blob_sha": proposal_sha,
            "original_draft": row.get("original_draft"),
            "original_draft_sha256": row.get("original_draft_sha256"),
        },
        "publication": {
            "phase2_registered": registered,
            "phase3_eligible": bool(row.get("phase3_eligible")) if registered else False,
            "proof_screening_accepted": bool(phase3 and phase3.get("outcome") == "plausible"),
            "publication_ready": False,
            "published": False,
        },
        "audit": {
            "migration_flags": sorted(set(flags)),
            "record_snapshots": snapshots or [],
        },
    }


def validate_records(records):
    problems = []
    seen = set()
    for r in records:
        cid = r.get("candidate_id")
        if cid in seen:
            problems.append({"candidate_id": cid, "issue": "duplicate_master_id"})
        seen.add(cid)
        if r.get("schema") != SCHEMA:
            problems.append({"candidate_id": cid, "issue": "schema_mismatch"})
        if r.get("source", {}).get("revision") != SOURCE_REV:
            problems.append({"candidate_id": cid, "issue": "wrong_source_revision"})
        for snap in r.get("audit", {}).get("record_snapshots", []):
            if sha256(snap["original_record_json"]) != snap["content_sha256"]:
                problems.append({"candidate_id": cid, "issue": "archived_snapshot_corruption"})
            try:
                json.loads(snap["original_record_json"])
            except json.JSONDecodeError:
                problems.append({"candidate_id": cid, "issue": "archived_snapshot_invalid_json"})
        if r["phase2"]["decision"] == "source_equivalence_approved":
            form = r["formulation"]
            if form["approved_content_sha256"] != content_digest(
                cid, r["source"]["revision"], form
            ):
                # A source-record digest disagreement is preserved as an explicit
                # publication blocker; it is not a lossless-migration failure.
                if "approved_formulation_digest_mismatch" not in r["audit"]["migration_flags"]:
                    problems.append({"candidate_id": cid, "issue": "unexplained_master_content_digest_mismatch"})
        if r["publication"]["published"] or r["publication"]["publication_ready"]:
            problems.append({"candidate_id": cid, "issue": "premature_publication_flag"})
    return problems


def migrate():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if registry.get("source_revision") != SOURCE_REV:
        raise RuntimeError("Authoritative registry revision mismatch")
    cache = {}

    def rows_indexed(path):
        if path not in cache:
            cache[path] = read_jsonl(path)
        return cache[path]

    def by_id(path):
        result = {}
        for row in rows_indexed(path):
            cid = row["candidate_id"]
            if cid in result:
                raise RuntimeError(f"Duplicate candidate ID in {path}: {cid}")
            result[cid] = row
        return result

    records, source_ids, worker_report, reports = {}, set(), [], []
    for worker in range(1, 5):
        frozen = frozen_queue(worker)
        active = json.loads((WORK / f"worker-{worker}/PENDING.json").read_text(encoding="utf-8"))
        if active.get("pending"):
            raise RuntimeError(f"Worker {worker} queue is not empty")
        batches = frozen["pending"]
        n, sections = 0, 0
        if len(batches) != EXPECTED_BATCHES[worker - 1]:
            raise RuntimeError(f"Worker {worker} unexpected batch count")
        for batch in batches:
            cp_path = WORK / f"worker-{worker}/checkpoints/{batch['batch_id']}.json"
            cp = json.loads(cp_path.read_text(encoding="utf-8"))
            expected_ids = [cid for sec in batch["sections"] for cid in sec["candidate_ids"]]
            if cp["candidate_ids"] != expected_ids:
                raise RuntimeError(f"Checkpoint does not match frozen ID ordering: {batch['batch_id']}")
            if cp["approved_count"] + cp["held_count"] != len(expected_ids):
                raise RuntimeError(f"Incomplete checkpoint: {batch['batch_id']}")
            section_ids = set()
            for sec in batch["sections"]:
                sections += 1
                rel = f"{sec['chapter']}/section-{sec['section_start_line']}.jsonl"
                decision_file = f"work/phase2-final-parallel/worker-{worker}/decisions/{rel}"
                drows = rows_indexed(decision_file)
                if [r["candidate_id"] for r in drows] != sec["candidate_ids"]:
                    raise RuntimeError(f"Decision file differs from frozen section: {decision_file}")
                # Immutable-input SHA verification on the exact files used in review.
                for file_key, sha_key in (
                    ("stage_b_file", "stage_b_blob_sha"),
                    ("phase3_review_file", "phase3_review_blob_sha"),
                    ("phase2_proposal_file", "phase2_proposal_blob_sha")
                ):
                    if git_blob(sec[file_key]) != sec[sha_key]:
                        raise RuntimeError(f"Immutable file changed: {sec[file_key]}")
                p3 = by_id(sec["phase3_review_file"])
                stageb = by_id(sec["stage_b_file"])
                proposal = by_id(sec["phase2_proposal_file"])
                for index, row in enumerate(drows, 1):
                    cid = row["candidate_id"]
                    if cid in source_ids:
                        raise RuntimeError(f"Worker candidate duplicated: {cid}")
                    source_ids.add(cid)
                    n += 1
                    if cid not in p3 or cid not in stageb or cid not in proposal:
                        raise RuntimeError(f"Missing Phase 3/Stage B/proposal material for {cid}")
                    b = stageb[cid]
                    if row.get("decision") == "source_equivalence_approved":
                        reviewed_form = row.get("final_content") or row
                        if any(b.get(k) != reviewed_form.get(k)
                               for k in ("statement", "hypotheses", "conclusions", "logical_form")):
                            reports.append({"candidate_id": cid, "issue": "stage_b_and_reviewed_formulation_disagree"})
                    snap = archived_snapshot("final_worker", decision_file, row, index)
                    record = canonical(
                        cid, row, origin="final_worker", worker=worker,
                        batch_id=batch["batch_id"],
                        section=sec["section_start_line"], phase3=p3[cid],
                        provenance={**sec, **row.get("referenced_immutable_inputs", {})},
                        snapshots=[snap],
                    )
                    records[cid] = record
                    section_ids.add(cid)
            if section_ids != set(expected_ids):
                raise RuntimeError(f"Section set disagrees with batch: {batch['batch_id']}")
        if n != EXPECTED_WORKER[worker - 1] or sections != EXPECTED_SECTIONS[worker - 1]:
            raise RuntimeError(f"Worker {worker} count mismatch: {n} candidates/{sections} sections")
        worker_report.append({"worker": worker, "candidates": n, "sections": sections,
                              "batches": len(batches)})
    if len(source_ids) != 3061:
        raise RuntimeError(f"Expected 3,061 worker IDs, found {len(source_ids)}")

    historical_ids, collisions = set(), []
    for path in registry["overlay_files"]:
        for i, row in enumerate(rows_indexed(path), 1):
            cid = row["candidate_id"]
            if cid in historical_ids:
                raise RuntimeError(f"Repeated historical authoritative candidate: {cid}")
            historical_ids.add(cid)
            snap = archived_snapshot("historical_authoritative", path, row, i)
            historical = canonical(cid, row, origin="historical_authoritative", snapshots=[snap])
            if cid in records:
                current = records[cid]
                collisions.append(cid)
                if (current["formulation"]["approved_content_sha256"]
                    != historical["formulation"]["approved_content_sha256"]
                    or current["phase2"]["decision"] != "source_equivalence_approved"):
                    historical["audit"]["migration_flags"].append("historical_worker_verdict_conflict")
                historical["audit"]["record_snapshots"].extend(current["audit"]["record_snapshots"])
                # Historical registration remains authoritative until explicit adjudication.
            records[cid] = historical

    output = [records[k] for k in sorted(records)]
    problems = validate_records(output)
    for rec in output:
        for issue in rec["audit"]["migration_flags"]:
            problems.append({"candidate_id": rec["candidate_id"], "issue": issue})
    problems.extend(reports)
    return output, {
        "schema": "maththm.master-migration-report.v1",
        "source_revision": SOURCE_REV,
        "frozen_worker_base": BASE,
        "expected_worker_candidates": 3061,
        "worker_counts": worker_report,
        "worker_unique_ids": len(source_ids),
        "historical_authoritative_ids": len(historical_ids),
        "historical_worker_overlaps": sorted(collisions),
        "unique_master_records": len(output),
        "phase2_decisions": dict(Counter(r["phase2"]["decision"] for r in output)),
        "migration_issues": problems,
        "migration_issue_types": dict(Counter(i["issue"] for i in problems)),
        "registration_changed": False,
        "published_catalog_changed": False,
        "old_decision_files_retained_pending_audit": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--write", action="store_true")
    selection.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.validate:
        records = read_jsonl(MASTER)
        problems = validate_records(records)
        if problems:
            raise SystemExit("Canonical-file validation failed: " + str(problems[:10]))
        print(json.dumps({"validated_records": len(records), "schema": SCHEMA,
                          "approved": sum(r["phase2"]["decision"] == "source_equivalence_approved" for r in records)}))
        return
    records, report = migrate()
    MASTER.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    MASTER.write_text("".join(json_text(r) + "\n" for r in records), encoding="utf-8")
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "migration_issues"},
                     indent=2, ensure_ascii=False))
    if report["migration_issues"]:
        print(f"Found {len(report['migration_issues'])} migration issues requiring classification; "
              f"see {REPORT.relative_to(ROOT)}")
        print("FIRST_25_EXCEPTIONS=" + json.dumps(report["migration_issues"][:25], ensure_ascii=False))
    # Issues do not remove records; none are silently approved or published.
    if validate_records(records):
        raise SystemExit("Master file has structural validation problems")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Apply verified mechanical exception resolutions to the materialized Phase 2 master.

Never reconstruct canonical records from legacy worker schemas or grant approval.
Usage: python scripts/reconcile_phase2_master.py --apply | --check
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import json
from pathlib import Path

from scripts.migrate_phase2_master import (
    ROOT, MASTER, SOURCE_REV, SCHEMA, FORM_FIELDS, content_digest,
    json_text, read_jsonl, sha256, validate_records,
)

WORK = ROOT / "work/phase2-canonical-migration"
QUEUES = WORK / "EXCEPTION_QUEUES.json"
REPORT = WORK / "RECONCILIATION_REPORT.json"
RESOLUTION_SCHEMA = "maththm.master-migration-resolution.v1"
EXPECTED_MASTER = 4132
EXPECTED_APPROVED = 3943
EXPECTED_HELD = 189
EXPECTED_RESOLVED = 70
EXPECTED_ISSUES = {
    "approved_formulation_digest_mismatch": 65,
    "original_source_digest_mismatch": 7,
    "phase3_reviewed_content_digest_mismatch": 5,
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def is_digest(s):
    return isinstance(s, str) and len(s) == 64 and all(c in "0123456789abcdef" for c in s)


def load_queue_and_resolutions(queue_path=QUEUES, work=WORK):
    queue = json.loads(Path(queue_path).read_text(encoding="utf-8"))
    require(queue.get("schema") == "maththm.phase2-canonical.exception-queues.v1", "Queue schema changed")
    require(queue.get("master_file") == "data/maththm_master.jsonl", "Wrong master target")
    require(queue.get("canonical_branch") == "work/phase2-canonical-migration", "Unexpected coordinator branch")
    require(queue.get("candidate_count") == EXPECTED_RESOLVED, "Exception count changed")
    require(len(queue.get("lanes", [])) == 4, "Expected four disjoint exception lanes")
    result, expected_flags = {}, Counter()
    for worker, lane in enumerate(queue["lanes"], 1):
        require(lane.get("worker") == worker, f"Lane {worker} moved")
        assigned = lane["records"]
        require(len(assigned) == lane["candidate_count"], f"Lane {worker} count changed")
        path = Path(work) / f"exceptions/worker-{worker}/RESOLUTIONS.jsonl"
        resolutions = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        require([r["candidate_id"] for r in resolutions] == [a["candidate_id"] for a in assigned],
                f"Worker {worker} missing/extra/out-of-order exception IDs")
        for assignment, resolution in zip(assigned, resolutions):
            cid = resolution["candidate_id"]
            require(cid not in result, f"Duplicate resolution ID {cid}")
            require(resolution.get("schema") == RESOLUTION_SCHEMA, f"Wrong resolution schema {cid}")
            require(resolution.get("worker") == worker, f"Wrong resolution lane {cid}")
            require(resolution.get("source_revision") == SOURCE_REV, f"Wrong pinned source {cid}")
            require(sorted(resolution.get("original_issue_types", [])) == sorted(assignment["issues"]),
                    f"Resolution issue types changed {cid}")
            require(resolution.get("resolution") == "mechanical_fix_verified" and
                    resolution.get("content_unchanged") is True, f"Unresolved or content-changing exception {cid}")
            require(isinstance(resolution.get("audit_note"), str) and resolution["audit_note"].strip(),
                    f"Missing forensic explanation {cid}")
            require(isinstance(resolution.get("evidence_files"), list) and resolution["evidence_files"],
                    f"Missing source references {cid}")
            for key in ("verified_approved_content_sha256", "verified_source_statement_sha256",
                        "verified_phase3_content_sha256"):
                require(is_digest(resolution.get(key)), f"Missing or invalid {key} for {cid}")
            expected_flags.update(assignment["issues"])
            result[cid] = resolution
    require(len(result) == EXPECTED_RESOLVED, "Not all exception IDs resolved")
    require(dict(expected_flags) == EXPECTED_ISSUES, "Exception flag totals changed")
    return result


def reconcile(records, resolutions):
    """In-place metadata-only update, deterministic and idempotent; no new authority."""
    require(len(records) == EXPECTED_MASTER, "Canonical master record count changed")
    ids = [r["candidate_id"] for r in records]
    require(ids == sorted(ids) and len(set(ids)) == len(ids), "Master IDs duplicated or unordered")
    require(Counter(r["phase2"]["decision"] for r in records) == {
        "source_equivalence_approved": EXPECTED_APPROVED,
        "source_equivalence_held": EXPECTED_HELD,
    }, "Phase 2 decisions changed")
    before = {r["candidate_id"]: (copy.deepcopy(r["source"]["original_statement_tex"]),
             copy.deepcopy({k: r["formulation"].get(k) for k in FORM_FIELDS}),
             copy.deepcopy(r["phase2"]), copy.deepcopy(r["publication"]),
             copy.deepcopy(r["provenance"])) for r in records}
    found = set()
    for r in records:
        cid = r["candidate_id"]
        if cid not in resolutions:
            continue
        found.add(cid)
        resolution = resolutions[cid]
        require(r["schema"] == SCHEMA, f"Schema changed {cid}")
        require(r["source"]["revision"] == SOURCE_REV, f"Revision changed {cid}")
        require(r["phase2"]["decision"] == "source_equivalence_approved", f"Held ID {cid}")
        expected_form_sha = content_digest(cid, SOURCE_REV, r["formulation"])
        require(resolution["verified_approved_content_sha256"] == expected_form_sha,
                f"Reviewed formulation does not match verified digest {cid}")
        expected_source_sha = sha256(r["source"]["original_statement_tex"])
        require(resolution["verified_source_statement_sha256"] == expected_source_sha,
                f"Source transcription does not match verified digest {cid}")
        require(resolution["verified_phase3_content_sha256"] == expected_form_sha,
                f"Phase 3 and Phase 2 reviewed formulation identity not established {cid}")
        audit = r["audit"]
        previous = audit.get("exception_resolution")
        if previous is not None:
            require(previous == resolution, f"Different prior resolution for {cid}")
            require(not audit.get("migration_flags"), f"Previously resolved flag has returned {cid}")
            require(r["formulation"]["approved_content_sha256"] == expected_form_sha and
                    r["source"]["original_statement_sha256"] == expected_source_sha and
                    r["phase3"]["verified_reviewed_content_sha256"] == expected_form_sha and
                    r["phase3"]["reviewed_content_digest_compatible"] is True,
                    f"Previously resolved metadata corrupted {cid}")
            continue
        flags = audit.get("migration_flags", [])
        require(sorted(flags) == sorted(resolution["original_issue_types"]),
                f"Unexpected unresolved migration flag(s) for {cid}: {flags}")
        audit["legacy_digest_values"] = {
            "source_statement_sha256": r["source"]["original_statement_sha256"],
            "approved_content_sha256": r["formulation"]["approved_content_sha256"],
            "phase3_reviewed_content_sha256_raw": r["phase3"]["reviewed_content_sha256_raw"],
            "phase3_reviewed_content_digest_compatible": r["phase3"]["reviewed_content_digest_compatible"],
        }
        audit["exception_resolution"] = copy.deepcopy(resolution)
        audit["resolved_migration_issues"] = sorted(flags)
        audit["migration_flags"] = []
        r["source"]["original_statement_sha256"] = expected_source_sha
        r["formulation"]["approved_content_sha256"] = expected_form_sha
        # Historical Phase 3 raw fingerprints and original snapshots remain unchanged.
        r["phase3"]["verified_reviewed_content_sha256"] = expected_form_sha
        r["phase3"]["reviewed_content_digest_compatible"] = True
    require(found == set(resolutions), "One or more verified exception IDs not in the master")
    for r in records:
        cid = r["candidate_id"]
        current = (r["source"]["original_statement_tex"],
                   {k: r["formulation"].get(k) for k in FORM_FIELDS},
                   r["phase2"], r["publication"], r["provenance"])
        require(current == before[cid], f"Reconciliation changed mathematical content/authority for {cid}")
    require(not validate_records(records), "Canonical structural validation failed after correction")
    require(not any(r["audit"].get("migration_flags") for r in records),
            "Unresolved migration flag exists")
    require(all(not r["publication"]["publication_ready"] and not r["publication"]["published"]
                for r in records), "Publication authority changed")
    return records


def check(records, resolutions):
    require(len(records) == EXPECTED_MASTER, "Canonical master count changed")
    require(not validate_records(records), "Master integrity failed")
    indexed = {r["candidate_id"]: r for r in records}
    require(len(indexed) == len(records), "Duplicate canonical ID")
    require(len(resolutions) == EXPECTED_RESOLVED, "Missing reconciled resolutions")
    for cid, res in resolutions.items():
        require(indexed[cid]["audit"].get("exception_resolution") == res,
                f"Missing permanent resolution evidence for {cid}")
        require(not indexed[cid]["audit"]["migration_flags"], f"Unresolved {cid}")
        require(indexed[cid]["formulation"]["approved_content_sha256"] ==
                content_digest(cid, SOURCE_REV, indexed[cid]["formulation"]),
                f"Invalid approved content digest {cid}")
    require(not any(r["audit"].get("migration_flags") for r in records),
            "Unexpected unresolved migration flag")
    require(Counter(r["phase2"]["decision"] for r in records) == {
        "source_equivalence_approved": EXPECTED_APPROVED,
        "source_equivalence_held": EXPECTED_HELD,
    }, "Decision totals changed")
    require(all(not r["publication"]["publication_ready"] and not r["publication"]["published"]
                for r in records), "Premature publication")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    resolutions = load_queue_and_resolutions()
    records = read_jsonl(MASTER)
    if args.apply:
        reconcile(records, resolutions)
        MASTER.write_text("".join(json_text(r) + "\n" for r in records), encoding="utf-8")
    check(records, resolutions)
    report = {
        "schema": "maththm.master-reconciliation-report.v1",
        "master_schema": SCHEMA,
        "master_records": len(records),
        "phase2_approved": EXPECTED_APPROVED,
        "phase2_held": EXPECTED_HELD,
        "verified_exception_ids": len(resolutions),
        "resolved_issue_occurrences": EXPECTED_ISSUES,
        "unresolved_migration_flags": 0,
        "mathematical_statements_changed": 0,
        "phase2_decisions_changed": 0,
        "publication_ready": 0,
        "legacy_source_snapshots_retained": True,
        "legacy_phase3_fingerprints_retained": True,
        "status": "mechanical_reconciliation_complete_not_publication_approval",
    }
    if args.apply:
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    else:
        require(json.loads(REPORT.read_text(encoding="utf-8")) == report,
                "Reconciliation report differs from canonical master")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""One-time, corpus-wide filtering of Stage A preparation packets.

This does NOT validate any mathematics. It reads Codex's independently
reviewed candidate IDs and authoritative approvals and writes per-chapter
candidate queues with those IDs already removed. Subsequent Stage A batches
must read STAGE_A_PENDING_CANDIDATES.jsonl rather than CANDIDATES.jsonl.
Original mechanically prepared files and their source hashes remain intact.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


REV = "a04446e57ec1fbc252a871afcec7752fb2807b14"
PENDING_FILE = "STAGE_A_PENDING_CANDIDATES.jsonl"
SECTION_FILE = "STAGE_A_PENDING_SECTION_IDS.jsonl"
REVIEWED_FILE = "CODEX_REVIEWED_CANDIDATES.jsonl"
SUMMARY_FILE = "STAGE_A_QUEUE_STATUS.json"


def jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(path)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def read_reviews(codex_root: Path) -> tuple[dict[str, dict], set[str]]:
    harvest = codex_root / "harvest"
    authoritative = json.loads(
        (harvest / "PHASE2_AUTHORITATIVE_REGISTRY.json").read_text(encoding="utf-8")
    )
    reviews = json.loads(
        (harvest / "phase2_calibration_2026-10-29" / "REVIEW_BATCHES.json")
        .read_text(encoding="utf-8")
    )
    if authoritative["source_revision"] != REV or reviews["source_revision"] != REV:
        raise ValueError("Codex review registry uses a different source revision")

    approved: set[str] = set()
    for relpath in authoritative["overlay_files"]:
        for row in jsonl(codex_root / relpath):
            candidate_id = row["candidate_id"]
            if row.get("source_revision") != REV or not row.get("phase2_validated"):
                raise ValueError("Unapproved or wrong-revision authoritative overlay")
            if candidate_id in approved:
                raise ValueError(f"Duplicate authoritative approval: {candidate_id}")
            approved.add(candidate_id)

    outcomes: dict[str, dict] = {}
    for batch in reviews["review_batches"]:
        relpath = batch["independent_validation"]
        for row in jsonl(codex_root / relpath):
            candidate_id = row["candidate_id"]
            verdict = row.get("independent_decision", row.get("decision"))
            if row.get("source_revision") != REV or not verdict:
                raise ValueError(f"Invalid review: {candidate_id}")
            if candidate_id in outcomes:
                raise ValueError(f"Candidate independently reviewed twice: {candidate_id}")
            outcomes[candidate_id] = {
                "independent_decision": verdict,
                "review_batch": batch["name"],
                "review_artifact": relpath,
            }
            if verdict == "source_equivalence_approved" and candidate_id not in approved:
                raise ValueError(f"Approved verdict without authoritative overlay: {candidate_id}")
            if verdict != "source_equivalence_approved" and candidate_id in approved:
                raise ValueError(f"Contradictory approval and hold: {candidate_id}")

    status_path = harvest / "phase2_chapters_2026-10-29" / "STATUS.json"
    if status_path.is_file():
        checkpoint = json.loads(status_path.read_text(encoding="utf-8"))
        if len(approved) != checkpoint["fully_phase2_validated"]:
            raise ValueError("Authoritative approvals do not reconcile to Codex status")

    return outcomes, approved


def generate(prepared_root: Path, codex_root: Path) -> dict:
    outcomes, approved = read_reviews(codex_root)
    index_path = prepared_root / "INDEX.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if index["source_revision"] != REV or index["prepared_candidates"] != 9675:
        raise ValueError("Expected full pinned preparation corpus, not a partial source")
    codex_sha = (codex_root / ".git").read_text().strip() if False else None
    all_ids: set[str] = set()
    all_pending: set[str] = set()
    all_excluded: set[str] = set()
    rows_summary = []
    for entry in index["chapters"]:
        chapter = entry["source_file"]
        folder = prepared_root / Path(chapter).stem
        originals = jsonl(folder / "CANDIDATES.jsonl")
        sections = jsonl(folder / "SECTIONS.jsonl")
        if len(originals) != entry["candidate_count"] or len(sections) != entry["section_count"]:
            raise ValueError(f"Original packet count mismatch: {chapter}")
        pending = []
        reviewed_rows = []
        for candidate in originals:
            candidate_id = candidate["candidate_id"]
            if candidate_id in all_ids:
                raise ValueError(f"Duplicate active ID: {candidate_id}")
            all_ids.add(candidate_id)
            if candidate_id in approved or candidate_id in outcomes:
                review = outcomes.get(candidate_id, {})
                reviewed_rows.append({
                    "candidate_id": candidate_id,
                    "source_file": chapter,
                    "source_label": candidate["source_label"],
                    "source_line": candidate["source_line"],
                    "codex_review_status": ("fully_phase2_validated" if candidate_id in approved
                                            else "independently_reviewed_unapproved"),
                    "independent_decision": review.get(
                        "independent_decision",
                        "historical_source_equivalence_approved",
                    ),
                    "review_batch": review.get("review_batch"),
                    "review_artifact": review.get("review_artifact"),
                })
                all_excluded.add(candidate_id)
            else:
                pending.append(candidate)
                all_pending.add(candidate_id)
        by_section: dict[int, list[str]] = {}
        for candidate in pending:
            by_section.setdefault(candidate["section_start_line"], []).append(candidate["candidate_id"])
        pending_sections = []
        for section in sections:
            ids = by_section.pop(section["section_start_line"], [])
            pending_sections.append({
                "source_file": chapter,
                "section_title": section["section_title"],
                "section_start_line": section["section_start_line"],
                "section_end_line": section["section_end_line"],
                "candidate_ids": ids,
                "pending_candidate_count": len(ids),
            })
        if by_section:
            raise ValueError(f"Candidate assigned to missing section: {chapter}")
        if len(pending) + len(reviewed_rows) != len(originals):
            raise ValueError(f"Source packet partition inconsistent: {chapter}")
        write_jsonl(folder / PENDING_FILE, pending)
        write_jsonl(folder / SECTION_FILE, pending_sections)
        write_jsonl(folder / REVIEWED_FILE, reviewed_rows)
        by_state = Counter(row["codex_review_status"] for row in reviewed_rows)
        summary = {
            "schema": "maththm.phase2.stage-a-pre-filter.v1",
            "source_revision": REV,
            "source_file": chapter,
            "candidate_count_original": len(originals),
            "stage_a_pending_count": len(pending),
            "codex_approved_count": by_state["fully_phase2_validated"],
            "codex_reviewed_unapproved_count": by_state["independently_reviewed_unapproved"],
            "section_count": len(sections),
            "source_packets_preserved": True,
            "approval_changes": 0,
            "pending_file": str((folder / PENDING_FILE).relative_to(prepared_root.parent.parent)),
            "reviewed_file": str((folder / REVIEWED_FILE).relative_to(prepared_root.parent.parent)),
        }
        (folder / SUMMARY_FILE).write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        rows_summary.append(summary)
    if len(all_ids) != index["prepared_candidates"]:
        raise ValueError("Active candidate count inconsistent with chapter index")
    if not approved <= all_ids or not set(outcomes) <= all_ids:
        raise ValueError("Codex reviewed candidate outside the pinned active population")
    if all_pending & all_excluded or all_pending | all_excluded != all_ids:
        raise ValueError("Filtered queues do not partition the full active corpus")
    if len(approved) != 655:
        # Frozen Codex baseline: updating this tool for a later review run should
        # include an explicit checkpoint refresh, not an accidental branch switch.
        raise ValueError(f"Expected 655 approved at pinned Codex baseline; got {len(approved)}")
    totals = {
        "schema": "maththm.phase2.stage-a-pre-filter-index.v1",
        "source_revision": REV,
        "codex_source_branch": "codex/phase2-validation",
        "candidate_count_original": len(all_ids),
        "codex_approved_count": len(approved),
        "codex_reviewed_unapproved_count": len(all_excluded - approved),
        "stage_a_pending_count": len(all_pending),
        "chapter_count": len(rows_summary),
        "sections_total": sum(row["section_count"] for row in rows_summary),
        "source_packets_preserved": True,
        "approval_changes": 0,
        "future_stage_a_input": PENDING_FILE,
        "future_stage_a_section_index": SECTION_FILE,
        "chapters": rows_summary,
    }
    (prepared_root / "STAGE_A_FILTER_INDEX.json").write_text(
        json.dumps(totals, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {k: v for k, v in totals.items() if k != "chapters"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared-root", type=Path,
                        default=Path("harvest/phase2_prepared/a04446e57ec1"))
    parser.add_argument("--codex-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(generate(args.prepared_root, args.codex_root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

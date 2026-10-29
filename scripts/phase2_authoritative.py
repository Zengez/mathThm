"""Reviewed Phase 2 overlays and fail-closed downstream consumption.

This module validates provenance and structure, never mathematical equivalence.
The explicit registry lists reviewer-approved artifacts; unlisted drafts cannot
become eligible. Historical Pass 1/2 data remain immutable.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path

REV = "a04446e57ec1fbc252a871afcec7752fb2807b14"
REGISTRY = Path("harvest/PHASE2_AUTHORITATIVE_REGISTRY.json")
CONTENT_FIELDS = ("candidate_id", "source_revision", "statement", "hypotheses",
                  "conclusions", "logical_form", "structured_cases", "equivalence_sides")


def content_digest(row):
    payload = {k: row.get(k) for k in CONTENT_FIELDS}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def validate_overlay(row):
    for field in ("candidate_id", "source_label", "statement", "semantic_review_note",
                  "original_source_statement_tex", "source_file", "original_draft",
                  "original_draft_sha256", "source_statement_sha256"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError(f"Phase 2 overlay requires {field}")
    if row.get("source_revision") != REV:
        raise ValueError("Phase 2 overlay has wrong pinned source revision")
    for field in ("hypotheses", "conclusions"):
        value = row.get(field)
        if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
            raise ValueError(f"Phase 2 overlay requires valid {field}")
    if not row["conclusions"]:
        raise ValueError("Phase 2 overlay requires conclusions")
    if row.get("phase2_validated") is not True or row.get("phase3_eligible") is not True:
        raise ValueError("Unapproved Phase 2 overlay cannot become eligible")
    if row.get("proof_reviewed") is True or row.get("published") is True:
        raise ValueError("Phase 2 overlays cannot assert proof review or publication")
    if row.get("duplicate_review_status") != "clear":
        raise ValueError("Phase 2 duplicate review gate not cleared")
    if not isinstance(row.get("source_line"), int) or row["source_line"] < 1:
        raise ValueError("Phase 2 overlay requires source line")
    expected = hashlib.sha256(row["original_source_statement_tex"].encode()).hexdigest()
    if expected != row["source_statement_sha256"]:
        raise ValueError("Phase 2 original source statement digest mismatch")
    if row.get("approved_content_sha256") != content_digest(row):
        raise ValueError("Phase 2 approved formulation digest mismatch")
    draft = Path(row["original_draft"])
    if not draft.is_file() or hashlib.sha256(draft.read_bytes()).hexdigest() != row["original_draft_sha256"]:
        raise ValueError("Phase 2 reconstruction provenance missing or changed")
    return row


def load_approved(registry=None):
    registry = Path(registry or REGISTRY)
    if not registry.is_file():
        raise RuntimeError("Phase 2 authoritative registry missing; Phase 3 is blocked")
    manifest = json.loads(registry.read_text())
    if manifest.get("source_revision") != REV or not isinstance(manifest.get("overlay_files"), list):
        raise ValueError("Invalid Phase 2 authoritative registry")
    pending_path = Path("harvest/CONSOLIDATED_CANDIDATES.jsonl")
    if not pending_path.is_file():
        raise RuntimeError("Provisional duplicate registry missing; Phase 3 is blocked")
    pending_duplicates = {json.loads(line)["canonical_candidate_id"]
                          for line in pending_path.read_text().splitlines() if line.strip()}
    result = {}
    for filename in manifest["overlay_files"]:
        path = Path(filename)
        if not path.is_file():
            raise RuntimeError(f"Registered Phase 2 overlays missing: {path}")
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            row = validate_overlay(json.loads(line))
            ident = row["candidate_id"]
            if ident in pending_duplicates:
                raise ValueError(f"Provisional duplicate requires mathematical adjudication: {ident}")
            if ident in result:
                raise ValueError(f"Duplicate authoritative Phase 2 candidate: {ident}")
            result[ident] = row
    return result


def apply_overlay(structured, overlay, *, raw=None):
    """Return the authoritative formulation while retaining intake metadata."""
    validate_overlay(overlay)
    if structured["candidate_id"] != overlay["candidate_id"]:
        raise ValueError("Phase 2 overlay candidate mismatch")
    if raw is not None:
        src = raw["source"]
        if src["revision"] != overlay["source_revision"] or src["filename"] != overlay["source_file"]:
            raise ValueError("Phase 2 overlay source provenance mismatch")
        if src.get("label") != overlay["source_label"]:
            raise ValueError("Phase 2 overlay source label mismatch")
        if src.get("statement_line") != overlay["source_line"]:
            raise ValueError("Phase 2 overlay source line mismatch")
        if raw.get("statement_tex", "").strip() != overlay["original_source_statement_tex"].strip():
            raise ValueError("Phase 2 overlay original source statement mismatch")
    result = copy.deepcopy(structured)
    for field in ("statement", "hypotheses", "conclusions", "logical_form", "structured_cases", "equivalence_sides"):
        result[field] = copy.deepcopy(overlay.get(field, [] if field.endswith("cases") or field.endswith("sides") else "single_implication"))
    result["context_status"] = "resolved"
    result["phase2_approved_content_sha256"] = overlay["approved_content_sha256"]
    result["statement_editorial_notes"] = overlay["semantic_review_note"]
    return result

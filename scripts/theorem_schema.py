"""Validation of accepted mathThm theorem records (no research or network access).

The outer v1 JSON shape remains compatible with the existing static site.
contract_revision=2 adds provenance and review-status separation. This module
checks STRUCTURE and traceability, never theorem truth or proof correctness.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = "maththm.theorems.v1"
CONTRACT_REVISION = 2
KINDS = {"theorem", "lemma", "proposition", "corollary", "other_result"}
INTAKE = {"cursory_screened"}
AUDIT = {"not_audited", "under_review", "reviewed_with_findings", "verified", "rejected"}
STATEMENT_BASIS = {
    "source_transcription", "editorial_restatement_unverified",
    "editorial_restatement_reviewed",
}
TRANSCRIPTION = {"preserved", "not_transcribed", "not_permitted"}
PROOF_SCREENING = {"cursory_screened", "audited", "verified"}
SOURCE_TAGS = {"initial_editorial", "source_literal", "editor_approved"}
ID = re.compile(r"^[a-z][a-z0-9_.-]{2,199}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate(corpus: dict) -> dict:
    """Raise ValueError with path on malformed accepted entries; return counts."""
    def bad(path, reason):
        raise ValueError(f"{path}: {reason}")

    def required_text(value, path):
        if not isinstance(value, str) or not value.strip():
            bad(path, "must be nonempty text")
        return value

    def https(value, path):
        required_text(value, path)
        parts = urlsplit(value)
        if parts.scheme != "https" or not parts.netloc or parts.username or parts.password:
            bad(path, "must be a public HTTPS source URL without credentials")

    def words(value, path):
        if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
            bad(path, "must be an array of nonempty strings")

    if not isinstance(corpus, dict) or corpus.get("schema") != SCHEMA:
        bad("catalog.schema", "unsupported theorem schema")
    if corpus.get("contract_revision") != CONTRACT_REVISION:
        bad("catalog.contract_revision", "must be 2")
    records = corpus.get("records")
    if not isinstance(records, list):
        bad("catalog.records", "must be a list")
    ids = set()
    counts = Counter()
    for i, r in enumerate(records):
        prefix = f"records[{i}]"
        if not isinstance(r, dict):
            bad(prefix, "must be an object")
        ident = required_text(r.get("id"), prefix+".id")
        if not ID.fullmatch(ident):
            bad(prefix+".id", "expected stable lowercase ID")
        if ident in ids:
            bad(prefix+".id", "duplicate ID")
        ids.add(ident)
        if r.get("entry_type") not in KINDS:
            bad(prefix+".entry_type", "unknown result type")
        if r.get("title") is not None and not isinstance(r.get("title"), str):
            bad(prefix+".title", "optional title must be text or null")
        required_text(r.get("area"), prefix+".area")
        required_text(r.get("statement"), prefix+".statement")
        https(r.get("source_url"), prefix+".source_url")
        for field in ("hypotheses","conclusions","hypothesis_tags","conclusion_tags"):
            words(r.get(field),prefix+"."+field)
        if not r["hypotheses"] or not r["conclusions"]:
            bad(prefix, "both structured search sides must be populated")
        if r.get("review_status") != "cursory_screened_unverified":
            # Historical display field kept for compatibility; audit is separate.
            bad(prefix+".review_status", "expected legacy draft display status")
        audit = r.get("mathematical_audit")
        if not isinstance(audit, dict) or audit.get("status") not in AUDIT:
            bad(prefix+".mathematical_audit", "expected explicit audit state")
        if audit.get("status") == "verified":
            bad(prefix+".mathematical_audit", "do not label verified while legacy UI says unverified")
        acquisition = r.get("acquisition")
        if not isinstance(acquisition, dict) or acquisition.get("status") not in INTAKE:
            bad(prefix+".acquisition", "accepted records require cursory proof screening")
        required_text(acquisition.get("batch_id"), prefix+".acquisition.batch_id")
        if not DATE.fullmatch(required_text(acquisition.get("collected_on"),prefix+".acquisition.collected_on")):
            bad(prefix+".acquisition.collected_on", "expected YYYY-MM-DD")
        provenance = r.get("statement_provenance")
        if not isinstance(provenance, dict) or provenance.get("basis") not in STATEMENT_BASIS:
            bad(prefix+".statement_provenance", "invalid statement provenance")
        if provenance.get("transcription_status") not in TRANSCRIPTION:
            bad(prefix+".statement_provenance.transcription_status", "invalid source transcription state")
        required_text(provenance.get("locator"), prefix+".statement_provenance.locator")
        text = provenance.get("source_text")
        if provenance["transcription_status"] == "preserved":
            required_text(text, prefix+".statement_provenance.source_text")
        elif text is not None:
            bad(prefix+".statement_provenance.source_text", "must be null when not transcribed")
        if provenance["basis"] == "source_transcription" and provenance["transcription_status"] != "preserved":
            bad(prefix+".statement_provenance", "source transcription requires preserved original")
        if not isinstance(provenance.get("editorial_notes"), str):
            bad(prefix+".statement_provenance.editorial_notes", "expected text, even if empty")
        annotations = r.get("tag_annotations")
        if not isinstance(annotations, list):
            bad(prefix+".tag_annotations", "expected list")
        defaults = r.get("tag_provenance_defaults")
        if not isinstance(defaults, dict) or any(defaults.get(side) not in SOURCE_TAGS for side in ("hypotheses","conclusions")):
            bad(prefix+".tag_provenance_defaults", "missing side-specific tag origins")
        for j,a in enumerate(annotations):
            if not isinstance(a,dict) or a.get("side") not in ("hypotheses","conclusions") or a.get("origin") not in SOURCE_TAGS:
                bad(prefix+f".tag_annotations[{j}]", "invalid side/origin")
            tag = required_text(a.get("tag"),prefix+f".tag_annotations[{j}].tag")
            if tag not in r["hypothesis_tags" if a["side"] == "hypotheses" else "conclusion_tags"]:
                bad(prefix+f".tag_annotations[{j}]", "annotation does not match a stored tag")
        hints=r.get("link_hints", [])
        if not isinstance(hints,list) or any(
            not isinstance(h,list) or len(h)!=2 or
            not all(isinstance(v,str) and v.strip() for v in h) for h in hints
        ):
            bad(prefix+".link_hints","expected [phrase, mathDef ID] pairs")
        exclusions=r.get("link_exclusions", [])
        words(exclusions,prefix+".link_exclusions")
        proofs = r.get("proofs")
        if not isinstance(proofs,list) or not proofs:
            bad(prefix+".proofs", "accepted result requires accessible proof")
        for j,p in enumerate(proofs):
            label=prefix+f".proofs[{j}]"
            if not isinstance(p,dict) or p.get("screening") not in PROOF_SCREENING:
                bad(label, "proof must be at least cursory screened")
            https(p.get("url"),label+".url")
            required_text(p.get("locator"),label+".locator")
            if not DATE.fullmatch(required_text(p.get("accessed_on"),label+".accessed_on")):
                bad(label+".accessed_on", "expected YYYY-MM-DD")
        proof_candidates = r.get("proof_candidates", [])
        if not isinstance(proof_candidates,list):
            bad(prefix+".proof_candidates", "must be list")
        for j,p in enumerate(proof_candidates):
            if not isinstance(p,dict) or p.get("status")!="uninspected":
                bad(prefix+f".proof_candidates[{j}]", "candidates must remain marked uninspected")
            https(p.get("url"),prefix+f".proof_candidates[{j}].url")
        sides=r.get("equivalence_sides",[])
        if not isinstance(sides,list) or any(not isinstance(side,list) or not side or
                                            not all(isinstance(v,str) and v.strip() for v in side)
                                            for side in sides):
            bad(prefix+".equivalence_sides", "must contain nonempty concept lists")
        counts[r["entry_type"]]+=1
    if "total" in corpus and corpus["total"]!=len(records):
        bad("catalog.total", "must equal number of records")
    return {"records":len(records),"by_type":dict(sorted(counts.items())),
            "review_status":"all accepted records cursory screened; correctness NOT certified"}


def load_validate(path: Path) -> dict:
    return validate(json.loads(Path(path).read_text(encoding="utf-8")))


if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file",nargs="?",default="data/theorems.json")
    args=parser.parse_args()
    print(json.dumps(load_validate(Path(args.file)),indent=2))

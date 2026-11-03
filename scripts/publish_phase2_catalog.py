#!/usr/bin/env python3
"""Publish authoritative Phase 2 decisions without re-reviewing mathematics.

Reads the permanent master directly; never rebuilds it from legacy worker files.
Four stable ID-prefix shards can be prepared independently, or --all can produce
every shard and the integrated site catalog in one deterministic run.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data/maththm_master.jsonl"
CATALOG = ROOT / "data/theorems.json"
OUT = ROOT / "work/phase2-final-publication"
SHARDS = OUT / "shards"
EXPECTED = 4132
REVIEW_DATE = "2026-11-03"
PREFIX = "candidate.stacks."
DECISION_APPROVED = "source_equivalence_approved"
DECISION_HELD = "source_equivalence_held"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
                    + "\n", encoding="utf-8")


def master_rows():
    records = [json.loads(line) for line in MASTER.read_text(encoding="utf-8").splitlines()
               if line.strip()]
    ids = [r["candidate_id"] for r in records]
    if len(records) != EXPECTED or len(set(ids)) != len(ids):
        raise ValueError("Master count or unique candidate IDs changed; stop integration")
    if sum(r["phase2"]["decision"] == DECISION_APPROVED for r in records) != 3943:
        raise ValueError("Approved decision count does not match reconciled master")
    return sorted(records, key=lambda r: r["candidate_id"])


def shard_for(cid):
    if not cid.startswith(PREFIX):
        raise ValueError("Unsupported canonical candidate ID: " + cid)
    return int(cid[len(PREFIX)], 16) // 4 + 1


def valid_https(url):
    if not isinstance(url, str) or not url.strip():
        return False
    p = urlsplit(url)
    return p.scheme == "https" and bool(p.netloc) and not p.username and not p.password


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def normalized(value):
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, list):
        return [normalized(x) for x in value]
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in sorted(value.items())}
    return value


def duplicate_key(theorem):
    # Same title, tags, or search-side text is NOT enough to merge theorem claims.
    return json.dumps(normalized([
        theorem["statement"], theorem["hypotheses"], theorem["conclusions"],
        theorem.get("equivalence_sides", []),
        theorem.get("structured_cases", []),
        theorem.get("logical_form"),
    ]), sort_keys=True, ensure_ascii=False)


def make_record(r):
    cid = r["candidate_id"]
    decision = r["phase2"]["decision"]
    if decision == DECISION_HELD:
        return {"candidate_id": cid, "status": "held", "reason": "phase2_explicit_hold"}
    if decision != DECISION_APPROVED:
        return {"candidate_id": cid, "status": "blocked", "reason": "unknown_phase2_decision"}

    f, s, p2, p3 = r["formulation"], r["source"], r["phase2"], r["phase3"]
    if not nonempty(f.get("statement")):
        return {"candidate_id": cid, "status": "blocked", "reason": "missing_approved_statement"}
    hyp, con = f.get("hypotheses"), f.get("conclusions")
    if (not isinstance(hyp, list) or
            not all(nonempty(t) for t in hyp) or
            not isinstance(con, list) or not con or
            not all(nonempty(t) for t in con)):
        return {"candidate_id": cid, "status": "blocked", "reason": "incomplete_search_sides"}
    if not valid_https(s.get("url")) or not nonempty(s.get("file")) or not s.get("line"):
        return {"candidate_id": cid, "status": "blocked", "reason": "invalid_source_reference"}
    if not nonempty(s.get("original_statement_tex")):
        return {"candidate_id": cid, "status": "blocked", "reason": "missing_source_statement"}
    label = s.get("label")
    if not nonempty(label):
        return {"candidate_id": cid, "status": "blocked", "reason": "missing_source_label"}
    kind = label.split("-", 1)[0].lower()
    if kind not in ("theorem", "lemma", "proposition", "corollary"):
        kind = "other_result"

    proof_url = p3.get("proof_url")
    has_screening = bool(p3.get("outcome") == "plausible" and
                         r["publication"].get("proof_screening_accepted"))
    if has_screening and not valid_https(proof_url):
        return {"candidate_id": cid, "status": "blocked", "reason": "invalid_screened_proof_url"}

    if has_screening:
        checked = p3.get("proof_checked_on")
        if not isinstance(checked, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", checked):
            return {"candidate_id": cid, "status": "blocked", "reason": "missing_proof_screening_date"}
        locator = p3.get("proof_locator")
        if not nonempty(locator):
            proof_file = p3.get("proof_file") or s["file"]
            start, end = p3.get("proof_start_line"), p3.get("proof_end_line")
            locator = f"{proof_file}:L{start}" + (f"-L{end}" if end else "") if start else s["file"]
        proofs = [{"url": proof_url, "locator": locator,
                   "screening": "cursory_screened", "accessed_on": checked}]
        proof_status = "phase3_screened"
    elif r["provenance"].get("origin") == "historical_authoritative":
        # The version-pinned Stacks source contains the statement and its vicinity.
        # This is a SOURCE REFERENCE, not a fabricated independent proof review.
        proofs = [{"url": s["url"], "locator": f"{s['file']}:L{s['line']}",
                   "screening": "source_reference_only"}]
        proof_status = "source_reference_only"
    else:
        return {"candidate_id": cid, "status": "blocked", "reason": "missing_essential_proof_reference"}

    sides = f.get("equivalence_sides")
    if sides is None:
        sides = []
    # Approved legacy equivalence sides use flat strings; wrapping each
    # phrase as a singleton search group is structural, not mathematical.
    if isinstance(sides, list) and all(isinstance(x, str) for x in sides):
        sides = [[x] for x in sides]
    if (not isinstance(sides, list) or
            any(not isinstance(group, list) or not group or
                not all(nonempty(x) for x in group) for group in sides)):
        return {"candidate_id": cid, "status": "blocked", "reason": "unsupported_equivalence_side_shape"}

    bare_name = label.split("-", 1)[-1].replace("-", " ").strip()
    title = kind.replace("_", " ").title() + " — " + (bare_name[0].upper() + bare_name[1:] if bare_name else "Unnamed")
    chapter = s["file"].removesuffix(".tex").replace("-", " ")
    ref = {
        "candidate_id": cid,
        "source_url": s["url"], "source_file": s["file"],
        "source_line": s["line"], "source_label": label,
        "source_revision": s.get("revision"),
        "source_statement_sha256": s.get("original_statement_sha256"),
        "phase2_decision": decision,
        "phase2_reviewer": p2.get("reviewer"),
        "phase2_reviewed_on": p2.get("reviewed_on"),
        "phase2_origin": r["provenance"].get("origin"),
        "phase2_batch_id": r["provenance"].get("batch_id"),
        "phase3_proof_url": proof_url,
        "phase3_screening": proof_status,
    }
    theorem = {
        "id": cid, "entry_type": kind,
        "title": title, "area": chapter.title(),
        "statement": f["statement"], "hypotheses": hyp, "conclusions": con,
        "hypothesis_tags": [], "conclusion_tags": [],
        "source_url": s["url"],
        "statement_provenance": {
            "basis": "editorial_restatement_reviewed",
            "transcription_status": "not_transcribed",
            "source_text": None,
            "locator": f"{s['file']}:L{s['line']} ({label})",
            "editorial_notes": "Phase 2 source-equivalence approved; original source wording retained in canonical master.",
        },
        "proofs": proofs,
        "acquisition": {
            "status": "phase2_approved",
            "batch_id": r["provenance"].get("batch_id") or "historical-authoritative",
            "collected_on": p2.get("reviewed_on") or REVIEW_DATE,
        },
        "mathematical_audit": {"status": "not_audited"},
        "review_status": "phase2_approved_" + proof_status,
        "tag_provenance_defaults": {"hypotheses": "editor_approved",
                                    "conclusions": "editor_approved"},
        "tag_annotations": [],
        "link_hints": [],
        "link_exclusions": [],
        "equivalence_sides": sides,
        "canonical_ids": [cid],
        "canonical_sources": [ref],
        "phase2_approval": {"decision": decision, "reviewer": p2.get("reviewer"),
                            "reviewed_on": p2.get("reviewed_on"),
                            "master_path": "data/maththm_master.jsonl"},
        "logical_form": f.get("logical_form"),
        "structured_cases": f.get("structured_cases") or [],
        "source_attribution": "The Stacks Project contributors",
        "statement_editorial": "Prior Phase 2 source-equivalence review accepted this restatement; proof correctness not independently audited.",
    }
    return {"candidate_id": cid, "status": "publishable", "theorem": theorem}


def generate_shard(number, all_rows=None):
    if not 1 <= number <= 4:
        raise ValueError("Shard must be in 1..4")
    rows = all_rows if all_rows is not None else master_rows()
    decisions = [make_record(r) for r in rows if shard_for(r["candidate_id"]) == number]
    result = {"schema": "maththm.publication-shard.v1", "worker": number,
              "source": "data/maththm_master.jsonl",
              "decisions": decisions,
              "counts": dict(sorted(Counter(x["status"] for x in decisions).items()))}
    dump_json(SHARDS / f"worker-{number}.json", result)
    return result


def merge_sources(primary, extra):
    primary["canonical_ids"] += extra["canonical_ids"]
    primary["canonical_sources"] += extra["canonical_sources"]
    existing = {(p["url"], p.get("locator")) for p in primary["proofs"]}
    for p in extra["proofs"]:
        if (p["url"], p.get("locator")) not in existing:
            primary["proofs"].append(p)
            existing.add((p["url"], p.get("locator")))


def integrate(all_rows=None):
    rows = all_rows if all_rows is not None else master_rows()
    source_ids = {r["candidate_id"] for r in rows}
    decisions = []
    for number in range(1, 5):
        shard = load_json(SHARDS / f"worker-{number}.json")
        if shard.get("schema") != "maththm.publication-shard.v1" or shard.get("worker") != number:
            raise ValueError("Invalid or misplaced publication shard")
        for d in shard["decisions"]:
            if shard_for(d["candidate_id"]) != number:
                raise ValueError("Worker crossed candidate-ID lane")
            decisions.append(d)
    ids = [d["candidate_id"] for d in decisions]
    if len(decisions) != len(rows) or len(set(ids)) != len(ids) or set(ids) != source_ids:
        raise ValueError("Missing, duplicated, or foreign canonical IDs in worker output")
    # Read the preexisting 20-prototype catalog from the frozen migration source,
    # rather than from the previous generated catalog.
    prototype_path = OUT / "prototype_baseline.json"
    prototype = load_json(prototype_path)
    previous = prototype["records"]
    if len(previous) != 20:
        raise ValueError("Unexpected prototype baseline")
    output = list(previous)
    used_ids = {r["id"] for r in output}
    signature_to_index = {}
    duplicates = []
    for d in sorted(decisions, key=lambda x: x["candidate_id"]):
        if d["status"] != "publishable":
            continue
        t = d["theorem"]
        if t["id"] in used_ids:
            raise ValueError("Canonical ID conflicts with a prototype theorem")
        key = duplicate_key(t)
        if key in signature_to_index:
            keep = output[signature_to_index[key]]
            merge_sources(keep, t)
            duplicates.append({"retained": keep["id"], "merged": t["id"]})
        else:
            signature_to_index[key] = len(output)
            output.append(t)
            used_ids.add(t["id"])
    statuses = Counter(d["status"] for d in decisions)
    blockers = [{"candidate_id": d["candidate_id"], "reason": d["reason"]}
                for d in decisions if d["status"] == "blocked"]
    report = {
        "schema": "maththm.publication-report.v1",
        "canonical_master_records": len(rows),
        "phase2_approved": sum(r["phase2"]["decision"] == DECISION_APPROVED for r in rows),
        "held": statuses["held"],
        "publishable_approved_records": statuses["publishable"],
        "blocked_approved_records": statuses["blocked"],
        "canonical_records_accounted_for": len(decisions),
        "prototype_records_preserved": len(previous),
        "mechanically_consolidated_duplicates": len(duplicates),
        "duplicate_pairs": duplicates,
        "published_new_catalog_entries": len(output) - len(previous),
        "published_catalog_entries_total": len(output),
        "source_reference_only_approved": sum(
            1 for d in decisions if d["status"] == "publishable"
            and d["theorem"]["canonical_sources"][0]["phase3_screening"] == "source_reference_only"),
        "phase3_screened_approved": sum(
            1 for d in decisions if d["status"] == "publishable"
            and d["theorem"]["canonical_sources"][0]["phase3_screening"] == "phase3_screened"),
        "unresolved_migration_flags": 0,
        "remaining_publication_exceptions": len(blockers),
    }
    if statuses["held"] != 189 or statuses["publishable"] + statuses["blocked"] != 3943:
        raise ValueError("Admission counts inconsistent with authoritative decisions")
    # Extra Wikipedia proof-section links are kept in a small durable overlay.
    # This is neither a proof audit nor a change to the canonical Stacks master.
    wikipedia_links_path = ROOT / "data/wikipedia_proof_links.json"
    if wikipedia_links_path.exists():
        wiki = load_json(wikipedia_links_path)
        if wiki.get("schema") != "maththm.wikipedia-proof-links.v1":
            raise ValueError("Unsupported Wikipedia proof-link overlay")
        by_id = {t["id"]: t for t in output}
        for ident, links in wiki["links_by_theorem_id"].items():
            theorem = by_id.get(ident)
            if theorem is None:
                continue  # Keep archived mapping; never map it to a different theorem.
            seen = set()
            extras = []
            for link in links:
                url = link.get("url")
                if not valid_https(url) or not url.startswith("https://en.wikipedia.org/wiki/"):
                    raise ValueError("Invalid Wikipedia proof URL in overlay")
                if url not in seen:
                    extras.append(link)
                    seen.add(url)
            if extras:
                theorem["proof_links"] = extras

    dump_json(CATALOG, {"schema": "maththm.theorems.v1", "contract_revision": 2,
                        "scope": "20 prototypes plus approved Phase 2 Stacks source-equivalence decisions; proof audit separate",
                        "total": len(output), "records": output})
    dump_json(OUT / "REPORT.json", report)
    dump_json(OUT / "BLOCKERS.json", blockers)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--worker", type=int, choices=range(1, 5))
    selection.add_argument("--integrate", action="store_true")
    selection.add_argument("--all", action="store_true")
    args = parser.parse_args()
    rows = master_rows()
    if args.worker:
        result = generate_shard(args.worker, rows)
        print(json.dumps({"worker": args.worker, "counts": result["counts"]}, sort_keys=True))
    else:
        if args.all:
            for n in range(1, 5):
                generate_shard(n, rows)
        print(json.dumps(integrate(rows), sort_keys=True))


if __name__ == "__main__":
    main()

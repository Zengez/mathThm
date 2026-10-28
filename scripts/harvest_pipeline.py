#!/usr/bin/env python3
"""Minimal three-pass mathThm acquisition workspace.

No LLM API, database, background worker, or external math research. Pass 2/3
packets are inputs for a human or model reviewer; scripts never claim to have
assessed mathematics. Only explicitly approved plausible records can publish.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path

if __package__:
    from .theorem_schema import validate as validate_accepted
else:
    from theorem_schema import validate as validate_accepted

STAGES = ("pass1", "pass2", "pass3", "needs_more_investigation")
OUTCOMES = {"plausible", "questionable", "rejected"}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                item = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{n}: invalid JSON: {e}") from e
            if not isinstance(item, dict):
                raise ValueError(f"{path}:{n}: expected JSON object")
            rows.append(item)
    return rows


def load_rows(path: Path, key: str) -> dict[str, dict]:
    result = {}
    for row in read_jsonl(path):
        name = row.get(key)
        if not isinstance(name, str) or not name:
            raise ValueError(f"{path}: missing {key}")
        if name in result:
            raise ValueError(f"{path}: repeated {key} {name}")
        result[name] = row
    return result


def atomic_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=path.parent, prefix=".pending-",
                                         suffix=".json", delete=False) as f:
            temp = Path(f.name)
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def merge_rows(path: Path, rows, key: str, *, replace: bool = False):
    """Atomic, deterministic keyed JSONL upsert. Conflict requires opt-in."""
    current = load_rows(path, key)
    for row in rows:
        item = row.get(key)
        if not isinstance(item, str) or not item:
            raise ValueError(f"row requires {key}")
        if item in current and current[item] != row and not replace:
            raise ValueError(f"conflicting {key} {item}; use explicit --replace")
        current[item] = row
    payload = "".join(json.dumps(current[k], ensure_ascii=False, sort_keys=True) + "\n"
                      for k in sorted(current))
    atomic_text(path, payload)
    return len(current)


def save_checkpoint(workdir: Path):
    """Derived local counts; source of truth remains stage files, not counters."""
    workdir = Path(workdir)
    rows = {stage: load_rows(workdir / (stage + ".jsonl"), "candidate_id")
            for stage in STAGES}
    payload = {
        "schema": "maththm.harvest-checkpoint.v1",
        "counts": {k: len(rows[k]) for k in STAGES},
        "pass3_outcomes": dict(sorted(Counter(x["outcome"] for x in rows["pass3"].values()).items())),
        "records_in_multiple_stages_expected": True,
        "source_of_truth": [stage + ".jsonl" for stage in STAGES],
    }
    atomic_text(workdir / "checkpoint.json", json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def needs_rows(raw: dict, structured: dict, reviewed: dict):
    result = []
    for ident, candidate in sorted(raw.items()):
        p2 = structured.get(ident)
        p3 = reviewed.get(ident)
        status, reason = None, None
        if p2 and p2.get("context_status") in ("needs_context", "needs_structure", "needs_classification", "not_result"):
            status = p2["context_status"]
            reason = p2.get("context_note") or "Requires manual investigation before Pass 3"
        if p3 and p3["outcome"] in ("questionable", "rejected"):
            status, reason = p3["outcome"], p3["reason"]
        if status:
            result.append({
                "candidate_id": ident, "status": status, "reason": reason,
                "source_url": candidate["source"]["source_url"],
                "proof_url": candidate["source"]["proof_url"],
                "source_confidence": candidate["source"]["confidence"],
                "proof_screening_outcome": p3["outcome"] if p3 else "not_scanned",
                "followup": "Manual investigation / alternate proof; do not auto-publish",
            })
    return result


def refresh_needs(workdir: Path):
    raw = load_rows(workdir / "pass1.jsonl", "candidate_id")
    p2 = load_rows(workdir / "pass2.jsonl", "candidate_id")
    p3 = load_rows(workdir / "pass3.jsonl", "candidate_id")
    # This queue is intentionally generated from canonical stage records.
    # Rebuilding cannot lose rejected and questionable proof decisions.
    merge_rows(workdir / "needs_more_investigation.jsonl", [], "candidate_id")
    payload = needs_rows(raw, p2, p3)
    atomic_text(workdir / "needs_more_investigation.jsonl",
                "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in payload))
    return save_checkpoint(workdir)


def parse_local_statements(source: Path):
    """One local file, one pass; no recursive cross-source link chasing."""
    if __package__:
        from .harvest_stacks import ENV, LABEL, COMMENT
    else:
        from harvest_stacks import ENV, LABEL, COMMENT
    text = COMMENT.sub("\n", source.read_text(encoding="utf-8"))
    result = {}
    for match in ENV.finditer(text):
        m = LABEL.search(match.group(2))
        if m:
            result[m.group(1)] = re.sub(r"\\label\{[^}]*\}", "", match.group(2)).strip()
    return result


def pass2_packets(args):
    w = Path(args.workdir)
    raw, reviewed = load_rows(w / "pass1.jsonl", "candidate_id"), load_rows(w / "pass2.jsonl", "candidate_id")
    packets = []
    local_cache = {}
    for ident, cand in sorted(raw.items()):
        if ident in reviewed:
            continue
        source = cand["source"]
        refs = cand.get("detected_local_references", [])[:args.max_local_references]
        local, unresolved = {}, []
        if refs and args.source_root:
            path = Path(args.source_root) / source["filename"]
            if path.is_file():
                if str(path) not in local_cache:
                    local_cache[str(path)] = parse_local_statements(path)
                for ref in refs:
                    text = local_cache[str(path)].get(ref)
                    if text and len(text) <= args.max_context_chars:
                        local[ref] = text
                    else:
                        unresolved.append(ref)
            else:
                unresolved = refs
        else:
            unresolved = refs
        packets.append({
            "candidate_id": ident,
            "source_url": source["source_url"],
            "statement_tex": cand["statement_tex"],
            "entry_type": cand["entry_type"],
            "source_confidence": source["confidence"],
            "local_context_excerpts": local,
            "unresolved_local_references": unresolved,
            "instruction": "Split statement only; do not research proofs or mathematics. If context cannot be resolved cheaply, set context_status=needs_context.",
            "required_decision": {
                "candidate_id": ident, "context_status": "resolved or needs_context",
                "statement": "faithful standalone editorial restatement for website",
                "hypotheses": ["assumptions"], "conclusions": ["result"],
                "hypothesis_tags": [], "conclusion_tags": [],
                "area": "subject", "context_note": "",
            },
        })
    atomic_text(w / "pass2_packets.jsonl", "".join(json.dumps(p,ensure_ascii=False,sort_keys=True)+"\n"
                    for p in packets))
    print(json.dumps({"stage": "pass2_packets", "packets": len(packets)}))


def apply_pass2(args):
    w = Path(args.workdir)
    raw = load_rows(w / "pass1.jsonl", "candidate_id")
    rows = []
    for decision in read_jsonl(Path(args.decisions)):
        ident = decision.get("candidate_id")
        if ident not in raw:
            raise ValueError(f"unknown Pass 1 candidate: {ident}")
        status = decision.get("context_status")
        if status not in ("resolved", "needs_context", "needs_structure", "needs_classification", "not_result"):
            raise ValueError(f"candidate {ident}: unknown Pass 2 status")
        note = decision.get("context_note", "")
        if not isinstance(note, str) or (status != "resolved" and not note.strip()):
            raise ValueError(f"candidate {ident}: unresolved Pass 2 requires explanation")
        # A needs-context candidate can be retained even without a confident split.
        values = {}
        for field in ("hypotheses", "conclusions", "hypothesis_tags", "conclusion_tags"):
            value = decision.get(field, [])
            if not isinstance(value, list) or any(not isinstance(v,str) or not v.strip() for v in value):
                raise ValueError(f"candidate {ident}: malformed {field}")
            values[field] = value
        statement = decision.get("statement", "")
        if not isinstance(statement, str) or (status == "resolved" and not statement.strip()):
            raise ValueError(f"candidate {ident}: resolved statement required")
        if status == "resolved" and (not values["hypotheses"] or not values["conclusions"]):
            raise ValueError(f"candidate {ident}: both searchable sides required")
        classification=decision.get("result_classification","mathematical_result")
        if classification not in ("mathematical_result", "not_mathematical_result", "uncertain"):
            raise ValueError(f"candidate {ident}: invalid result classification")
        if status == "resolved" and classification != "mathematical_result":
            raise ValueError(f"candidate {ident}: only mathematical results may be marked resolved")
        review_method=decision.get("review_method","editorial")
        if review_method not in ("editorial","mechanical_syntax"):
            raise ValueError(f"candidate {ident}: invalid Pass 2 review method")
        rows.append({
            "candidate_id": ident, "context_status": status,
            "context_note": note, "result_classification":classification,
            "review_method":review_method,
            "split_confidence":decision.get("split_confidence","editorial" if review_method=="editorial" else "syntax_only"),
            "statement": statement,
            "title": decision.get("title"),
            "area": decision.get("area") or "Unclassified",
            "statement_basis": "editorial_restatement_unverified",
            "statement_editorial_notes": decision.get("statement_editorial_notes", ""),
            "local_context_used": decision.get("local_context_used", []),
            **values,
        })
    total = merge_rows(w / "pass2.jsonl", rows, "candidate_id", replace=args.replace)
    state = refresh_needs(w)
    print(json.dumps({"stage":"pass2_apply", "applied":len(rows),"structured_total":total,
                      "needs_investigation":state["counts"]["needs_more_investigation"]}))


def pass3_packets(args):
    w = Path(args.workdir)
    raw, structured, reviewed = (
        load_rows(w / "pass1.jsonl","candidate_id"),
        load_rows(w / "pass2.jsonl","candidate_id"),
        load_rows(w / "pass3.jsonl","candidate_id"))
    packets = []
    for ident,p2 in sorted(structured.items()):
        if ident in reviewed or p2["context_status"] != "resolved" or p2.get("result_classification","mathematical_result") != "mathematical_result":
            continue
        cand = raw[ident]
        proof = cand["source"]
        source_path = Path(args.source_root) / proof["filename"]
        excerpt, truncated = "", True
        if source_path.is_file():
            lines = source_path.read_text(encoding="utf-8").splitlines()
            start = proof["proof_start_line"]-1
            last = proof.get("proof_end_line")
            portion = "\n".join(lines[start:min(last or len(lines),len(lines))])
            truncated = last is None or len(portion) > args.max_proof_chars
            excerpt = portion[:args.max_proof_chars]
        packets.append({
            "candidate_id": ident, "statement": p2["statement"],
            "source_confidence": proof["confidence"],
            "proof_url": proof["proof_url"], "proof_locator": proof["proof_locator"],
            "proof_excerpt": excerpt, "excerpt_truncated": truncated,
            "proof_end_marker_found": cand["proof_end_marker_found"],
            "instruction": "Quick proof-plausibility scan ONLY. Plausible if no evident issue after full brief scan; questionable if necessary follow-up exceeds budget; rejected only for a positive identifiable issue. Do not claim proof is verified.",
            "required_decision": {"candidate_id": ident,
                "outcome": "plausible | questionable | rejected",
                "scan_completed": False,
                "reason": "brief evidence-based note, required if questionable or rejected",
                "proof_checked_on": date.today().isoformat()},
        })
    atomic_text(w/"pass3_packets.jsonl",
                "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in packets))
    print(json.dumps({"stage":"pass3_packets","packets":len(packets),
                      "truncated":sum(x["excerpt_truncated"] for x in packets)}))


def apply_pass3(args):
    w = Path(args.workdir)
    raw = load_rows(w/"pass1.jsonl","candidate_id")
    structured=load_rows(w/"pass2.jsonl","candidate_id")
    packets=load_rows(w/"pass3_packets.jsonl","candidate_id")
    decisions=[]
    for d in read_jsonl(Path(args.decisions)):
        ident = d.get("candidate_id")
        if ident not in raw or ident not in structured or structured[ident]["context_status"]!="resolved":
            raise ValueError(f"candidate {ident}: Pass 2 must be resolved before Pass 3")
        outcome=d.get("outcome")
        if outcome not in OUTCOMES:
            raise ValueError(f"candidate {ident}: invalid outcome")
        completed=d.get("scan_completed")
        reason=d.get("reason","")
        if not isinstance(completed,bool) or not isinstance(reason,str):
            raise ValueError(f"candidate {ident}: invalid scan-completed/reason")
        checked=d.get("proof_checked_on")
        if not isinstance(checked,str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}",checked):
            raise ValueError(f"candidate {ident}: checked_on must be YYYY-MM-DD")
        if outcome == "plausible" and not completed:
            raise ValueError(f"candidate {ident}: plausible requires full brief scan")
        if outcome == "plausible" and packets.get(ident,{}).get("excerpt_truncated") and not d.get("full_proof_reviewed_externally"):
            raise ValueError(f"candidate {ident}: truncated proof packet cannot be plausible without full external review")
        if outcome != "plausible" and not reason.strip():
            raise ValueError(f"candidate {ident}: questionable/rejected requires concrete explanation")
        if outcome == "plausible" and not raw[ident]["proof_end_marker_found"] and not d.get("manually_verified_proof_completion"):
            raise ValueError(f"candidate {ident}: proof end not detected; completion must be explicitly confirmed")
        decisions.append({
            "candidate_id":ident, "outcome":outcome, "scan_completed":completed,
            "reason":reason, "proof_checked_on":checked,
            "source_confidence":raw[ident]["source"]["confidence"],
            "proof_screening_confidence":"brief_scan_only",
            "mathematical_audit":"not_audited",
            "proof_url":raw[ident]["source"]["proof_url"],
        })
    total=merge_rows(w/"pass3.jsonl",decisions,"candidate_id",replace=args.replace)
    state=refresh_needs(w)
    print(json.dumps({"stage":"pass3_apply","decisions":len(decisions),"total":total,
                      "outcomes":state["pass3_outcomes"],
                      "needs_more_investigation":state["counts"]["needs_more_investigation"]}))


def provisional_record(raw: dict, structured: dict, checked: dict):
    if structured["context_status"]!="resolved" or structured.get("result_classification","mathematical_result")!="mathematical_result" or checked["outcome"]!="plausible":
        raise ValueError("only fully structured plausible evidence may be promoted")
    if not checked["scan_completed"]:
        raise ValueError("proof scan not completed")
    s=raw["source"]
    return {
        "id": raw["candidate_id"].replace("candidate.stacks.","thm.stacks.",1),
        "entry_type": raw["entry_type"],
        "title": structured.get("title") or (raw["entry_type"].title()+" (Stacks: "+str(s["label"] or s["statement_locator"])+")"),
        "area": structured["area"],
        "statement": structured["statement"],
        "hypotheses":structured["hypotheses"],"conclusions":structured["conclusions"],
        "hypothesis_tags":structured["hypothesis_tags"],
        "conclusion_tags":structured["conclusion_tags"],
        "source_url":s["source_url"],
        "statement_editorial":"Unverified editorial restatement. Original source at the pinned Stacks reference.",
        "statement_provenance":{
            "basis":"editorial_restatement_unverified",
            "transcription_status":"not_transcribed","source_text":None,
            "locator":s["statement_locator"],
            "editorial_notes":structured["statement_editorial_notes"] or "Original source kept in the local Pass 1 candidate; website displays a restatement."
        },
        "proofs":[{
            "url":s["proof_url"],"locator":s["proof_locator"],
            "screening":"cursory_screened","accessed_on":checked["proof_checked_on"],
        }],
        "acquisition":{"status":"cursory_screened","batch_id":raw["batch_id"],
                       "collected_on":raw["collected_on"]},
        "mathematical_audit":{"status":"not_audited"},
        "tag_provenance_defaults":{"hypotheses":"initial_editorial","conclusions":"initial_editorial"},
        "tag_annotations":[],"review_status":"cursory_screened_unverified",
        "source_attribution":{
            "source_name":s["name"],"author":s["attribution"],
            "license_note":s["license_note"],"source_revision":s["revision"],
        },
        "intake_candidate_id":raw["candidate_id"],
        "source_confidence":s["confidence"],
        "proof_plausibility":{"status":"plausible","screening":"brief_scan_only",
                             "reason":checked["reason"]},
    }


def promote(args):
    w=Path(args.workdir)
    raw=load_rows(w/"pass1.jsonl","candidate_id")
    structured=load_rows(w/"pass2.jsonl","candidate_id")
    review=load_rows(w/"pass3.jsonl","candidate_id")
    catalog_path=Path(args.catalog)
    output=Path(args.output)
    if catalog_path.resolve()==output.resolve() and not args.in_place:
        raise ValueError("publishing in place requires explicit --in-place")
    catalog=json.loads(catalog_path.read_text(encoding="utf-8"))
    validate_accepted(catalog)
    existing_ids={r["id"]:r for r in catalog["records"]}
    before=len(catalog["records"])
    for ident, p3 in sorted(review.items()):
        if p3["outcome"]!="plausible":
            continue
        if ident not in raw or ident not in structured:
            raise ValueError(f"incomplete candidate data: {ident}")
        accepted=provisional_record(raw[ident],structured[ident],p3)
        old=existing_ids.get(accepted["id"])
        if old:
            if old!=accepted:
                raise ValueError(f"existing accepted theorem changed; no silent overwrite: {ident}")
            continue
        existing_ids[accepted["id"]]=accepted
        catalog["records"].append(accepted)
    catalog["total"]=len(catalog["records"])
    validate_accepted(catalog)
    atomic_text(output, json.dumps(catalog,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"stage":"promote","accepted_records":catalog["total"],
                      "new_provisional_records":len(catalog["records"])-before,
                      "output":str(output),"published_to_site":False}))
    # Even an explicit in-place update modifies only the local source file;
    # the website is published separately via reviewed Git commit/Pages CI.


def make_parser():
    p=argparse.ArgumentParser(description=__doc__)
    subs=p.add_subparsers(dest="cmd",required=True)
    for name in ("pass2-packets","pass2-apply","pass3-packets","pass3-apply","promote","status"):
        q=subs.add_parser(name)
        q.add_argument("--workdir",required=True)
        if name in ("pass2-apply","pass3-apply"):
            q.add_argument("--decisions",required=True)
            q.add_argument("--replace",action="store_true",
                           help="Explicitly replace an existing decision with the same candidate ID")
        if name=="pass2-packets":
            q.add_argument("--source-root")
            q.add_argument("--max-local-references",type=int,default=2)
            q.add_argument("--max-context-chars",type=int,default=1400)
        if name=="pass3-packets":
            q.add_argument("--source-root",required=True)
            q.add_argument("--max-proof-chars",type=int,default=7500)
        if name=="promote":
            q.add_argument("--catalog",default="data/theorems.json")
            q.add_argument("--output",required=True)
            q.add_argument("--in-place",action="store_true")
    return p


def main():
    args=make_parser().parse_args()
    if args.cmd=="pass2-packets":
        pass2_packets(args)
    elif args.cmd=="pass2-apply":
        apply_pass2(args)
    elif args.cmd=="pass3-packets":
        pass3_packets(args)
    elif args.cmd=="pass3-apply":
        apply_pass3(args)
    elif args.cmd=="promote":
        promote(args)
    elif args.cmd=="status":
        print(json.dumps(save_checkpoint(Path(args.workdir)),indent=2))


if __name__=="__main__":
    main()

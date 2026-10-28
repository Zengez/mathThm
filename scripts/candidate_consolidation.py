"""Adjudicate exact-phrase duplicate leads and retain all proof/source provenance.

Source data is *never* overwritten. The accepted merges are an editorial,
source-scope-based decision list; proof validity is not inspected here.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from scripts import harvest_pipeline as p

def norm(s):
    s=re.sub(r"\\label\{[^{}]*\}","",s or "")
    s=re.sub(r"\\(?:begin|end)\{[^{}]*\}","",s)
    return re.sub(r"\s+","",s).lower()

POLICY=Path("harvest/DUPLICATE_MERGE_POLICY_2026-10-28.json")
REVIEW=Path("harvest/DUPLICATE_GROUP_REVIEW_2026-10-28.jsonl")
MERGED=Path("harvest/CONSOLIDATED_CANDIDATES.jsonl")
DECISIONS=Path("harvest/DUPLICATE_ADJUDICATION_DECISIONS_2026-10-28.jsonl")
CROSSWALK=Path("harvest/DUPLICATE_CANDIDATE_CROSSWALK_2026-10-28.jsonl")

def merge_candidate_sources(active_records, *, batches, archive_ids):
    """Return reduced canonical candidates and merge metrics; write provenance.

    A short, isolated fixture without the real policy remains unmerged. The
    production batch is fail-closed: a missing reviewed policy is an error.
    """
    candidates={x["candidate_id"]:x for x in active_records}
    if not POLICY.exists():
        if len(candidates)>5000:
            raise RuntimeError("Missing reviewed mathThm duplicate policy")
        return active_records,{"merged_groups":0,"merged_aliases":0,
                               "source_active_total":len(candidates)}

    policy=json.loads(POLICY.read_text(encoding="utf-8"))
    review=p.read_jsonl(REVIEW)
    assert policy["schema"]=="maththm.prototype-duplicate-adjudication.v1"
    assert len(review)==102
    assert {g["group_number"] for g in review}==set(range(1,103))
    approved={g["group_number"]:g for g in policy["approved_merge_groups"]}
    separated={g["group_number"]:g for g in policy["explicit_separations"]}
    assert len(approved)==8 and not (approved.keys()&separated.keys())

    original={};structured={}
    for batch in batches:
        w=Path("harvest/batches")/batch
        for ident,item in p.load_rows(w/"pass1.jsonl","candidate_id").items():
            assert ident not in original
            original[ident]=item
        for ident,item in p.load_rows(w/"pass2.jsonl","candidate_id").items():
            assert ident not in structured
            structured[ident]=item
    assert set(candidates)<=set(original)&set(structured)
    aliases={}
    consolidated=[]
    decisions=[]
    crosswalk=[]
    for group in review:
        number=group["group_number"]
        members=sorted(r["id"] for r in group["records"])
        assert len(members)==group["size"]==len(set(members))
        assert set(members)<=set(candidates)
        if number not in approved:
            special=separated.get(number)
            files=sorted({original[k]["source"]["filename"] for k in members})
            if special:
                reason=special["reason"]
                specificity="explicit_contextual_distinction"
            elif any(r"\ref{" in original[k].get("statement_tex","") for k in members):
                reason="Locally scoped source references or standing situations may differ: "+", ".join(files)
                specificity="source_local_reference"
            else:
                reason=policy["fallback_separation_reason"]+" Files: "+", ".join(files)
                specificity="ambient_not_proven_identical"
            decisions.append({"group_number":number,"candidate_ids":members,
                              "decision":"keep_separate",
                              "reason":reason,
                              "review_basis":specificity})
            continue

        # Exact source wording and matching complete indexed logical structure
        # alone are not sufficient: this approval was also scoped to a shared
        # explicitly stated mathematical setting in the policy.
        texts=[norm(original[k].get("statement_tex","")) for k in members]
        statements=[norm(structured[k]["statement"]) for k in members]
        if len(set(texts))!=1 or len(set(statements))!=1:
            raise ValueError(f"group {number}: wording has diverged")
        forms={structured[k].get("logical_form") or "single_implication" for k in members}
        if len(forms)!=1:
            raise ValueError(f"group {number}: genuinely different logical forms")
        for fld in ("hypotheses","conclusions","equivalence_sides",
                    "structured_cases"):
            values=[structured[k].get(fld) for k in members]
            if any(v!=values[0] for v in values[1:]):
                raise ValueError(f"group {number}: different {fld}; cannot merge")
        if len({original[k]["entry_type"] for k in members})!=1:
            raise ValueError(f"group {number}: distinct entry types")
        if len({original[k]["source"]["label"] for k in members})!=1:
            raise ValueError(f"group {number}: distinct provenance labels")
        assert not (set(members)&set(archive_ids))
        primary=members[0]
        refs=[]
        proofs=[]
        for ident in members:
            if ident in aliases:
                raise ValueError(f"Overlapping duplicate mergers: {ident}")
            s=original[ident]["source"]
            refs.append({
                "candidate_id":ident,
                "source_name":s.get("name"),
                "source_attribution":s.get("attribution"),
                "license_note":s.get("license_note"),
                "source_revision":s.get("revision"),
                "source_filename":s.get("filename"),
                "source_label":s.get("label"),
                "source_url":s["source_url"],
                "statement_locator":s.get("statement_locator"),
                "entry_type":original[ident]["entry_type"],
                "statement_tex":original[ident].get("statement_tex",""),
            })
            proofs.append({
                "candidate_id":ident,
                "proof_url":s["proof_url"],
                "proof_locator":s.get("proof_locator"),
                "source_filename":s.get("filename"),
                "source_revision":s.get("revision"),
                "proof_end_marker_found":original[ident].get("proof_end_marker_found"),
                "status":"uninspected",
            })
            crosswalk.append({
                "candidate_id":ident,"canonical_candidate_id":primary,
                "is_primary":ident==primary,"merge_group":number,
            })
            if ident!=primary:
                aliases[ident]=primary
        if len({x["source_url"] for x in refs})!=len(refs):
            raise ValueError(f"group {number}: repeated source citation")
        if len({x["proof_url"] for x in proofs})!=len(proofs):
            raise ValueError(f"group {number}: repeated proof URL")
        case={
            "canonical_candidate_id":primary,
            "member_candidate_ids":members,
            "merge_group":number,
            "merge_reason":approved[number]["reason"],
            "statement":structured[primary]["statement"],
            "hypotheses":structured[primary]["hypotheses"],
            "conclusions":structured[primary]["conclusions"],
            "hypothesis_tags":structured[primary].get("hypothesis_tags",[]),
            "conclusion_tags":structured[primary].get("conclusion_tags",[]),
            "logical_form":structured[primary].get("logical_form"),
            "equivalence_sides":structured[primary].get("equivalence_sides",[]),
            "structured_cases":structured[primary].get("structured_cases",[]),
            "source_references":refs,
            "proof_references":proofs,
            "status":"Pass 2 source-structured, Pass 3 not screened",
            "proof_validity_assessed":False,
        }
        consolidated.append(case)
        decisions.append({"group_number":number,"candidate_ids":members,
                          "canonical_candidate_id":primary,
                          "decision":"merge",
                          "reason":approved[number]["reason"],
                          "review_basis":"identical explicit mathematical setting and complete indexed logical form"})

    assert len(decisions)==102
    assert sum(x["decision"]=="merge" for x in decisions)==8
    assert not set(aliases)&set(archive_ids)
    retained=[r for r in active_records if r["candidate_id"] not in aliases]
    assert len(retained)+len(aliases)==len(active_records)
    assert {r["candidate_id"] for r in retained}==set(candidates)-set(aliases)
    assert len({x["candidate_id"] for x in crosswalk})==sum(len(x["member_candidate_ids"]) for x in consolidated)
    consolidated.sort(key=lambda x:x["canonical_candidate_id"])
    crosswalk.sort(key=lambda x:x["candidate_id"])
    decisions.sort(key=lambda x:x["group_number"])
    for path,rows in ((MERGED,consolidated),(DECISIONS,decisions),(CROSSWALK,crosswalk)):
        p.atomic_text(path,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in rows))
    metrics={
        "merged_groups":len(consolidated),
        "merged_aliases":len(aliases),
        "source_active_total":len(active_records),
        "reviewed_flagged_groups":len(decisions),
        "flagged_groups_kept_separate":sum(x["decision"]=="keep_separate" for x in decisions),
        "merged_records_file":str(MERGED),
        "decision_file":str(DECISIONS),
        "crosswalk_file":str(CROSSWALK),
        "alternate_proofs_retained_uninspected":len(aliases),
        "every_original_source_and_proof_preserved":True,
    }
    return retained,metrics

def load_merged_by_canonical():
    return p.load_rows(MERGED,"canonical_candidate_id") if MERGED.exists() else {}

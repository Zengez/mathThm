#!/usr/bin/env python3
"""Conservative logical-form QC on newly promoted inherited-context Pass 2 only.

Source-only audits do NOT certify theorem validity. Complex iff/equivalence,
editorial TODOs, or unrepresented converse clauses must stay on the higher-
thinking needs_context queue; do not call these ordinary implications.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from collections import Counter
from scripts import harvest_pipeline as p
from scripts.pass2_context_source_probe import BATCHES

NEW=("pass2_context_global_reference_decisions.jsonl",
     "pass2_context_global_section_decisions.jsonl")
PLACEHOLDER=re.compile(r"(?i)\b(?:add more here|to do|we should prove|exercise for the reader)\b")
IFF=re.compile(r"(?i)\bif\s+and\s+only\s+if\b")
EQUIV=re.compile(r"(?i)\b(?:the\s+following\s+(?:conditions\s+)?are\s+equivalent|"
                 r"following\s+conditions\s+are\s+equivalent|"
                 r"equivalent\s+conditions\s+of|"
                 r"these\s+(?:conditions|statements)\s+are\s+equivalent)\b")
CONVERSE=re.compile(r"(?i)\bconversely\b")

def problem(record):
    s=record["statement"]
    if PLACEHOLDER.search(s):return "source contains an editorial placeholder"
    logical=record.get("logical_form","")
    sides=record.get("equivalence_sides",[])
    valid_equiv=("equivalence" in logical and bool(sides) and
        all(x in record["hypotheses"] and x in record["conclusions"]
            for group in sides for x in group))
    if (IFF.search(s) or EQUIV.search(s)) and not valid_equiv:
        return "biconditional or enumerated equivalence not completely indexed bidirectionally"
    if CONVERSE.search(s) and not valid_equiv:
        return "converse statement needs independently represented logical direction"
    return None

def main():
    report=[];totals=Counter()
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        current=p.load_rows(w/"pass2.jsonl","candidate_id")
        introduced=set()
        for name in NEW:
            file=w/name
            if file.exists():
                introduced.update(p.load_rows(file,"candidate_id"))
        downgraded=[];issues=Counter()
        for ident in sorted(introduced):
            r=current[ident]
            if r["context_status"]!="resolved":continue
            if not r.get("split_confidence","").startswith((
                "pinned_global_reference_source_grammar",
                "pinned_global_section_setup_source_grammar")):
                continue
            why=problem(r)
            if not why:continue
            issues[why]+=1
            downgraded.append({
                **r,"context_status":"needs_context",
                "context_note":"Higher-thinking Pass 2 required: "+why+
                    ". Exact cited source context remains attached for individual review.",
                "hypotheses":[],"conclusions":[],
                "hypothesis_tags":[],"conclusion_tags":[],
                "logical_form":"deferred_inherited_context_complex_logic",
                "equivalence_sides":[],"structured_cases":[],
                "split_confidence":"source_context_recovered_logical_form_deferred",
                "review_method":"editorial",
                "statement_editorial_notes":
                    "Previously recovered named source retained; source statement "+
                    "not promoted because logical-form quality control identified: "+why+
                    ". No proof read or mathematics validity claim."})
        if downgraded:
            path=w/"pass2_context_semantic_qc_deferred.jsonl"
            p.atomic_text(path,"".join(json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n" for x in downgraded))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(path),replace=True))
        final=p.load_rows(w/"pass2.jsonl","candidate_id")
        assert set(current)==set(final)
        for ident,old in current.items():
            if ident not in {r["candidate_id"] for r in downgraded}:
                assert final[ident]["context_status"]==old["context_status"]
        assert not p.load_rows(w/"pass3.jsonl","candidate_id")
        totals.update(r["context_status"] for r in final.values())
        report.append({"batch":batch,"new_context_introduced":len(introduced),
            "deferred_for_logical_review":len(downgraded),
            "reasons":dict(sorted(issues.items()))})
    assert sum(totals.values())==10987
    out={"batches":report,"quality_deferred_total":sum(r["deferred_for_logical_review"] for r in report),
         "status_totals":dict(sorted(totals.items())),
         "proofs_read":False,"published_catalog_unchanged":True}
    p.atomic_text(Path("harvest/PASS2_CONTEXT_LOGICAL_QC_2026-10-28.json"),
                  json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True,indent=2))
if __name__=="__main__":main()

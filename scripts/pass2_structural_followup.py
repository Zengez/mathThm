#!/usr/bin/env python3
"""Second bounded Pass 2 structural-only review of surviving difficult Stacks statements.

Allows explicit equivalences WITH separately scoped source addenda. Preserves
bidirectional indexing, never treats a conditional addendum as equivalent,
and never makes enumerated jointly necessary conditions independent.
All decisions remain provisional (no proof or mathematical truth audit).
"""
from __future__ import annotations
import argparse,json,re
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.pass2_context_source_probe import BATCHES
from scripts.pass2_hard_structures import enum_blocks,list_items,mask_math,logical_item
from scripts.pass2_remaining_targeted import source_body
from scripts.pass2_structural_refined import (make,PLACEHOLDER,EXTERNAL,
    EQUIV,IFF,INTRO,IF_THEN)

EXTRA_START=re.compile(r"(?i)^(?:In\s+cases?\s*\(|In\s+(?:these|those)\s+cases?|"
    r"Moreover\b|In\s+particular\b|Furthermore\b|If\s+this\s+is\s+true\b|"
    r"Such\s+an?\b|In\s+this\s+case\b|The\s+(?:correspondence|value|result)\b)")
GENERAL_ADDENDUM=re.compile(r"(?i)^(?:Moreover|In\s+particular|Furthermore|Such\s+an?)\b")
CASE_ADDENDUM=re.compile(r"(?i)^(?:In\s+cases?\s*\(|In\s+(?:these|those)\s+cases?|In\s+this\s+case)\b")
CONJUNCTIVE_IF=re.compile(r"(?i)\bif\s+and\s+only\s+if\s+(?:"
    r"the\s+(?:following\s+)?(?:conditions?|properties|statements?)\s+"
    r"(?:are\s+satisfied|hold|are\s+fulfilled)|"
    r"(?:both|all)\s+of\s+the\s+following\s+conditions\s+hold)\s*[:.]?\s*$")
UNIV=re.compile(r"(?is)^(?:For|Given)\s+.{10,600}?\b(?:there\s+(?:exists?|are|is)|"
                r"we\s+(?:have|obtain)|the\s+(?:natural|canonical)\s+map)\b")

def equivalence_with_tail(base,body,block,items):
    a,b=block
    pre=body[:a].strip()
    tail=body[b:].strip()
    if not 2<=len(items)<=18 or any("\\begin{enumerate}" in x for x in items):
        return None
    if any(PLACEHOLDER.search(x) for x in items):return None
    hits=list(EQUIV.finditer(mask_math(pre)))
    if len(hits)!=1:return None
    marker=hits[0]
    if pre[marker.end():].strip(" \n\t:.;"):return None
    setup=pre[:marker.start()].strip(" \n\t:.;")
    if not setup or not INTRO.match(setup):return None
    if not tail or len(tail)>800 or not EXTRA_START.match(tail):return None
    if PLACEHOLDER.search(tail) or EQUIV.search(tail):return None
    # A tail is *not* part of the equivalence. Keep clause explicitly separate.
    if IFF.search(mask_math(tail)):
        return None
    clauses=[{"logical_form":"source_equivalence","hypotheses":[setup]+items,
              "conclusions":list(items),
              "source_clause":body[a:b]}]
    if CASE_ADDENDUM.match(tail):
        clauses.append({"logical_form":"source_scoped_addendum",
              "hypotheses":[setup],"conclusions":[tail],
              "source_clause":tail,
              "scope_note":"Applies only in the source-named cases; do not distribute across all equivalent conditions"})
    elif GENERAL_ADDENDUM.match(tail):
        clauses.append({"logical_form":"source_additional_assertion",
              "hypotheses":[setup],"conclusions":[tail],
              "source_clause":tail})
    else:
        # e.g. 'If this is true then...' bound to equivalent conditions.
        clauses.append({"logical_form":"conditional_on_equivalent_conditions",
              "hypotheses":[setup,tail.split("then")[0].strip()],
              "conclusions":[tail],"source_clause":tail,
              "scope_note":"Additional consequent, NOT an equivalence side"})
    return make(base,[setup]+list(items),list(items)+[tail],
                "source_equivalence_with_additional_scoped_consequence",
                "Explicit equivalent conditions indexed both ways; following source addendum is NOT equivalent to them",
                cases=clauses,equivalence=items)

def iff_with_joint_list(base,body,block,items):
    a,b=block
    pre=body[:a].strip()
    tail=body[b:].strip(" .\n\t")
    if tail or len(items)<2 or len(items)>12:return None
    m=CONJUNCTIVE_IF.search(mask_math(pre))
    if not m:return None
    leading=pre[:m.start()].strip()
    if not leading or not INTRO.match(leading):return None
    # Identify an explicit final THEN or completed setup before the P iff (Q1 and Q2).
    t=list(IF_THEN.finditer(mask_math(leading)))
    if len(t)!=1:return None
    i=t[0]
    setup=leading[:i.start()].strip()
    left=leading[i.end():].strip().rstrip(", ")
    if not setup or not left or IFF.search(mask_math(left)):return None
    right="All of the following conditions hold:\n"+body[a:b]
    return make(base,[setup,left,right],[left,right],
                "equivalence_with_joint_enumerated_condition",
                "P is equivalent to the CONJUNCTION of conditions, not each separately",
                cases=[{"logical_form":"equivalence_with_conjunctive_side",
                         "hypotheses":[setup,left,right],
                         "conclusions":[left,right],
                         "source_clause":body}],
                equivalence=[left,right])

def universal_context_assertion(base,body):
    # Explicit source quantifier: retain the quantifier as a context SEARCH
    # phrase, not as a substantive extra hypothesis.
    if len(body)>820 or "\\begin" in body or IFF.search(mask_math(body)):
        return None
    if not re.match(r"(?i)^(?:For\s+(?:every|any|all|each)|Given\s+any)\b",body):
        return None
    if PLACEHOLDER.search(body) or re.search(r"(?i)\b(?:conversely|moreover|add\s+more)\b",body):
        return None
    masked=mask_math(body)
    marker=re.search(r"(?i)\b(?:there\s+(?:exists?|are|is)|"
                     r"we\s+(?:obtain|have)|the\s+(?:canonical|natural)\s+map)\b",masked)
    if not marker or marker.start()<22:return None
    context=body[:marker.start()].strip(" ,;")
    result=body[marker.start():].strip()
    if not context or not result or context.endswith(("if","or","and","that","such that")):
        return None
    if re.search(r"(?i)\b(?:then|whenever|provided)\b",context):
        return None
    return make(base,[context],[result],
                "source_universal_context_assertion",
                "Source quantification indexed as context; no new conditional premise invented")

def classify(base):
    body,_=source_body(base["statement"])
    if not body or PLACEHOLDER.search(body) or EXTERNAL.search(body):
        return None,"source_placeholder_or_inherited_context"
    blocks=enum_blocks(body)
    if blocks is None:return None,"unbalanced_enumerate"
    if len(blocks)==1:
        items=list_items(body,blocks[0])
        if not items:return None,"unparseable_list"
        for fn in (equivalence_with_tail,iff_with_joint_list):
            got=fn(base,body,blocks[0],items)
            if got:return got,fn.__name__
    elif not blocks:
        got=universal_context_assertion(base,body)
        if got:return got,"universal_context_assertion"
    return None,"needs_editorial_structural_review"

def main():
    allcounts=Counter()
    total=0
    for b in BATCHES:
        w=Path("harvest/batches")/b
        rows=p.load_rows(w/"pass2.jsonl","candidate_id")
        before=Counter(q["context_status"] for q in rows.values())
        changed=[];blocks=Counter()
        for ident,item in sorted(rows.items()):
            if item["context_status"]!="needs_structure":continue
            d,reason=classify(item)
            if d:changed.append(d);blocks[reason]+=1
        if changed:
            path=w/"pass2_structural_followup_decisions.jsonl"
            p.atomic_text(path,"".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in changed))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(path),replace=True))
        now=p.load_rows(w/"pass2.jsonl","candidate_id")
        counts=Counter(v["context_status"] for v in now.values())
        assert counts["needs_context"]==before["needs_context"]
        assert counts["needs_structure"]==before["needs_structure"]-len(changed)
        assert not p.load_rows(w/"pass3.jsonl","candidate_id")
        p.atomic_text(w/"pass2_structural_followup_summary.json",
            json.dumps({"batch":b,"before_structure":before["needs_structure"],
                "new_resolved":len(changed),"remaining_structure":counts["needs_structure"],
                "recovery_methods":dict(sorted(blocks.items())),"proofs_read":False},
            indent=2,sort_keys=True)+"\n")
        allcounts.update(counts);total+=len(changed)
    assert sum(allcounts.values())==10987
    out={"newly_resolved":total,"statuses":dict(sorted(allcounts.items())),
          "proofs_read":False,"catalog_unchanged":True}
    p.atomic_text(Path("harvest/PASS2_STRUCTURAL_FOLLOWUP_2026-10-28.json"),
                  json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()

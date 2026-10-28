#!/usr/bin/env python3
"""Bounded Pass 2 source-level semantic statement grammar, not mathematical proofs.

Targets a carefully limited set of *currently* structurally unresolved source
statements. Distinguishes closure under base change/composition, source lists of
conditional clauses, explicit casewise sufficient conditions, and completed
setup clauses before an assertion. All source LaTeX is preserved verbatim.
Does not turn unconditional existential claims into fake implications.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from collections import Counter

from . import harvest_pipeline as p
from .pass2_context_source_probe import BATCHES
from .pass2_remaining_targeted import source_body
from .pass2_hard_structures import (mask_math,enum_blocks,list_items,logical_item,
    AMBIGUOUS,INTRO,EQUIV)

CROSS_CONTEXT=re.compile(r"(?i)\b(?:as\s+(?:above|before)|in\s+the\s+situation\s+above|"
                         r"with\s+(?:the\s+)?notation\s+as\s+in|"
                         r"under\s+the\s+assumptions\s+of)\b")
SOURCE_TOP=re.compile(r"(?i)^(?:Let|Suppose|Assume|Fix|Consider|Given|Take|For)\b")
PROPERTIES=re.compile(r"(?i)^The\s+base\s+change\s+of\s+(?P<subject>.+?)\s+is\s+(?P<predicate>[^.]+)\.?$")
COMPOSITION=re.compile(
    r"(?i)^(?:(?:The\s+)?compositions?\s+of)\s+(?P<subject>.+?)\s+"
    r"(?P<verb>is|are|satisfies)\s+(?P<predicate>.+?)\.?$")
BASED=re.compile(r"(?i)^(?P<subject>(?:[A-Z][^\n.]{6,300}?))\s+"
                 r"(?:are|is)\s+preserved\s+by\s+base\s+change\.?$")
SPLIT= re.compile(r"\b(?:The|This|These|There|We|Any|Every|Each|A|An)\b",re.I)
ALTERNATES=re.compile(r"(?i)\bin\s+each\s+of\s+the\s+following\s+cases\b")
ELLIPSIS=re.compile(r"(?i)\b(?:and\s+so\s+on|etc\.?|add\s+more\s+here|"
                    r"and\s+so\s+forth|to\s+do)\b")

def make(original,h,c,form,reason,cases=None,equiv=None):
    if not h or not c or any(not isinstance(x,str) or not x.strip() for x in h+c):
        return None
    return {**original,"hypotheses":h,"conclusions":c,
            "context_status":"resolved","context_note":"",
            "review_method":"editorial",
            "split_confidence":"bounded_source_semantic_indexing_unverified",
            "logical_form":form,
            "equivalence_sides":[[s] for s in (equiv or [])],
            "structured_cases":cases or [],
            "statement_editorial_notes":"Pass 2 limited statement-level logical reading: "+reason+
                 ". Hypothesis source subjects are search fields, not artificially asserted premises. "+
                 "Original source unchanged; no proof scan or independent mathematical validation."}

def closure_statement(base,body):
    if len(body)>800 or "\\begin{" in body or CROSS_CONTEXT.search(body):
        return None
    s=re.sub(r"\s+"," ",body).strip()
    # Do not collapse two different source assertions into one scope.
    segments=re.split(r"\.\s+(?=[A-Z])",s)
    if len(segments)>2:return None
    cases=[];hypotheses=[];conclusions=[]
    for k,part in enumerate(segments):
        if k and re.fullmatch(r"(?i)The same (?:holds|is true) for [^.]+\.?",part):
            # Scope is inherited from first sentence; source-specific
            # property is retained as an independent follow-up case.
            cases.append({"logical_form":"parallel_closure_property",
                "hypotheses":[segments[0],"source follow-up property: "+part],
                "conclusions":[part],"source_clause":part})
            hypotheses.append("source follow-up property: "+part)
            conclusions.append(part)
            continue
        m=PROPERTIES.fullmatch(part) or COMPOSITION.fullmatch(part) or BASED.fullmatch(part)
        if not m:return None
        subject=m.group("subject").strip()
        if not subject or len(subject)>350 or "if and only if" in part.lower():return None
        # Explicit subject property is the hypothesis search target; the
        # entire statement is retained in results to avoid rewording an
        # algebraic/geometric condition.
        h=subject
        hypotheses.append(h)
        conclusions.append(part if part.endswith(".") else part+".")
        cases.append({"logical_form":"closure_source_assertion",
                      "hypotheses":[h],"conclusions":[conclusions[-1]],
                      "source_clause":part})
    if not cases:return None
    return make(base,hypotheses,conclusions,
                "source_closure_property",
                "Explicit closure-under-operation source subject plus its full result",
                cases=cases)

def explicit_casewise(base,body):
    blocks=enum_blocks(body)
    if blocks is None or len(blocks)!=1:return None
    a,b=blocks[0]
    pre=body[:a].strip()
    tail=body[b:].strip(" \n\t.")
    if tail or not SOURCE_TOP.match(pre):return None
    m=ALTERNATES.search(pre)
    if not m:return None
    items=list_items(body,blocks[0])
    if not items or len(items)>16 or any(ELLIPSIS.search(z) for z in items):
        return None
    context=pre[:m.start()].strip()
    conclusion=pre[m.end():].strip(" :\n\t")
    if not context or not conclusion or not re.search(r"\b(?:is|has|have|are|can|admits|exists?)\b",mask_math(conclusion),re.I):
        return None
    cases=[{"logical_form":"alternative_sufficient_condition",
            "hypotheses":[context,item],"conclusions":[conclusion],
            "source_clause":item} for item in items]
    return make(base,[context]+items,[conclusion],
                "source_alternative_sufficient_conditions",
                "Each source-listed case separately suffices; no conjunction of alternative premises",
                cases=cases)

def explicit_listed_conditional_results(base,body):
    blocks=enum_blocks(body)
    if blocks is None or len(blocks)!=1:return None
    a,b=blocks[0]
    pre=body[:a].strip()
    post=body[b:].strip(" \n\t.")
    if post or len(body)>3200:return None
    if re.search(r"(?i)\b(?:suppose|assume|given)\s*:?\s*$",pre):
        return None
    if re.search(r"(?i)\b(?:the\s+following\s+are\s+equivalent|"
                 r"the\s+following\s+conditions\s+hold|one\s+of\s+the\s+following)\b",pre):
        return None
    items=list_items(body,blocks[0])
    if not items or len(items)>14 or any(ELLIPSIS.search(x) for x in items):
        return None
    # Avoid title-only metadata becoming the shared assumptions.
    m=re.search(r"\b(?:Let|Given|Suppose|Fix|Consider|Assume)\b",mask_math(pre),re.I)
    if not m:return None
    shared=pre[m.start():].strip()
    if not shared or len(shared)<10:return None
    # Do not turn an enumerated definition of objects into theorem conclusions.
    if re.search(r"(?i)\b(?:definition|defined\s+as|called|we\s+say)\b",pre):
        return None
    cases=[logical_item(z,shared) for z in items]
    # Each clause must have a meaningful mathematical assertion, and
    # we retain per-case implication semantics. No editorial placeholder.
    if any(len(z["source_clause"])<14 or
           (not re.search(r"(?i)\b(?:is|are|has|have|if|then|can|exists?|"
                             r"there|commutes|agrees|equal|becomes|gives|induces)\b",
                             mask_math(z["source_clause"]))) for z in cases):
        return None
    h=[shared];c=[]
    for case in cases:
        h.extend(z for z in case["hypotheses"][1:] if z not in h)
        c.extend(case["conclusions"])
    return make(base,h,c,"source_enumerated_assertions",
                "Individual source assertions and conditional subcases retained, not merged into one implication",
                cases=cases)

def explicit_setup_followed_by_claim(base,body):
    if not SOURCE_TOP.match(body) or len(body)>1900:return None
    if "\\begin{enumerate}" in body or CROSS_CONTEXT.search(body):
        return None
    mtext=mask_math(body)
    # Find first completed initial setup sentence preceding an asserted claim.
    boundaries=list(re.finditer(r"\.\s+(?=(?:The|This|These|There|We|Any|Every|Each|A|An)\b)",mtext))
    for sep in boundaries:
        a,b=body[:sep.end()].strip(),body[sep.end():].strip()
        if not a or not b or re.search(r"(?i)\bif\s+and\s+only\s+if\b",mtext):
            continue
        if any(ELLIPSIS.search(z) for z in (a,b)):continue
        if re.search(r"(?i)\b(?:then|whenever|provided)\b",mask_math(a)):continue
        if re.match(r"^(?:The|This|These|There|We)\b",b,re.I):
            if re.search(r"(?i)\b(?:is|are|has|have|there|exists?|"
                         r"gives|maps|commutes|induces|can)\b",mask_math(b)):
                return make(base,[a],[b],"source_setup_followed_by_assertion",
                     "Completed explicit setup followed by source assertion")
    return None

def try_one(base):
    body,_=source_body(base["statement"])
    if AMBIGUOUS.search(body) or ELLIPSIS.search(body) or CROSS_CONTEXT.search(body):
        return None,"source_edit_or_outside_context"
    for fn in (closure_statement,explicit_casewise,
               explicit_listed_conditional_results,explicit_setup_followed_by_claim):
        result=fn(base,body)
        if result:return result,fn.__name__
    return None,"genuine_or_complex_structure"

def run(args):
    total=0
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        rows=p.load_rows(w/"pass2.jsonl","candidate_id")
        changed=[];forms=Counter();blocked=Counter()
        for ident,v in sorted(rows.items()):
            if v["context_status"]!="needs_structure":continue
            r,why=try_one(v)
            if r:changed.append(r);forms[why]+=1
            else:blocked[why]+=1
        if changed:
            path=w/"pass2_semantic_source_decisions.jsonl"
            p.atomic_text(path,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in changed))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(path),replace=True))
        latest=p.load_rows(w/"pass2.jsonl","candidate_id")
        summary={"batch":batch,"new_resolved":len(changed),
            "forms":dict(sorted(forms.items())),
            "deferred_reasons":dict(sorted(blocked.items())),
            "statuses":dict(sorted(Counter(v["context_status"] for v in latest.values()).items())),
            "proofs_read":False,"mathematical_validity_assessed":False}
        p.atomic_text(w/"pass2_semantic_source_summary.json",json.dumps(summary,indent=2,sort_keys=True)+"\n")
        print(json.dumps(summary,sort_keys=True))
        total+=len(changed)
    print(json.dumps({"all_newly_resolved":total}))

if __name__=="__main__":
    run(argparse.ArgumentParser().parse_args())

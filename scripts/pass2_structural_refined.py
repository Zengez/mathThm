#!/usr/bin/env python3
"""Source-conservative Pass 2 review of *only* currently needs_structure cases.

Source-grammar decisions are not mathematical truth/proof verification.
Equivalences are bidirectional search records. Conditional list clauses are
individually scoped. Where the current search contract requires a nonempty
hypothesis, never invent one for a genuinely unconditional assertion.
"""
from __future__ import annotations
import argparse,json,re
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.pass2_context_source_probe import BATCHES
from scripts.pass2_remaining_targeted import source_body
from scripts.pass2_hard_structures import (enum_blocks,list_items,mask_math,
                                            safe_setup,logical_item)

PLACEHOLDER=re.compile(r"(?i)\b(?:add\s+more\s+here|to\s+do|we\s+should\s+prove|"
                       r"exercise\s+for\s+the\s+reader|and\s+so\s+on|"
                       r"and\s+so\s+forth)\b")
EXTERNAL=re.compile(r"(?i)\b(?:in\s+the\s+situation\s+above|as\s+above|"
                    r"assumptions\s+and\s+notation\s+as\s+in|"
                    r"with\s+notation\s+as\s+above)\b")
EQUIV=re.compile(r"(?i)\b(?:the\s+following(?:\s+conditions|\s+statements)?\s+"
                 r"are\s+equivalent|following\s+conditions\s+are\s+equivalent)\b")
IFF=re.compile(r"(?i)\bif\s+and\s+only\s+if\b")
INTRO=re.compile(r"(?i)^(?:Let|Fix|Suppose|Assume|Consider|Given|Take|For)\b")
ASSERT_START=re.compile(r"(?i)^(?:The|This|These|There|We|Every|Any|Each|"
                         r"All|An|A)\b")
ASSUME_END=re.compile(r"(?i)\b(?:assume|suppose|given|provided|under\s+the\s+following\s+conditions)\s*:?\s*$")
ANY_WHEN=re.compile(r"(?i)^(?:If|Whenever)\b")
IF_THEN=re.compile(r"(?i)\bthen\b")
SINGLE_SUBJECT=re.compile(
    r"(?is)^(?P<subject>(?:Every|Each|All|Any|The|A|An)\s+.{5,240}?)\s+"
    r"(?P<verb>is|are|has|have|admits|can\s+be|defines|satisfies|splits)\s+(?P<rest>.+)$")
MULTI_TAIL=re.compile(r"(?i)\b(?:moreover|conversely|in\s+addition|"
                      r"furthermore|and\s+in\s+this\s+case)\b")

def make(base,h,c,form,note,*,cases=None,equivalence=None):
    if not h or not c or any(not isinstance(s,str) or not s.strip() for s in h+c):
        return None
    sides=[[x] for x in (equivalence or [])]
    if sides and not all(v in h and v in c for group in sides for v in group):
        return None
    return {**base,"hypotheses":h,"conclusions":c,
         "logical_form":form,"structured_cases":cases or [],
         "equivalence_sides":sides,"context_status":"resolved","context_note":"",
         "review_method":"editorial",
         "split_confidence":"bounded_source_logical_structure_unverified",
         "statement_editorial_notes":"Pass 2 source-only structural interpretation: "+note+
             ". Source statement preserved verbatim. No mathematical validity/proof review."}

def explicit_equivalence(base,body,block,items):
    a,b=block
    before=body[:a].strip()
    tail=body[b:].strip(" .\n\t")
    if tail or len(items)>18 or len(items)<2 or any("\\begin{enumerate}" in x for x in items):
        return None
    markers=list(EQUIV.finditer(mask_math(before)))
    if len(markers)!=1:return None
    m=markers[0]
    if before[m.end():].strip(" \n\t:.;"):return None
    context=before[:m.start()].strip(" \n\t:.;")
    if not context:return None
    # Some source statements put the entire setup in an initial phrase
    # "Let ...". Do not convert the items into a conjunction or imply
    # pairwise equivalence when the header asserts it explicitly.
    if re.search(r"(?i)\b(?:iff|either|one\s+of|in\s+each\s+case)\b",context):
        return None
    cases=[{"logical_form":"equivalence","hypotheses":[context]+list(items),
             "conclusions":list(items),"source_clause":body[a:b]}]
    return make(base,[context]+list(items),list(items),
                "enumerated_equivalence_with_source_context",
                "All listed conditions are mutually equivalent and indexed on both sides",
                cases=cases,equivalence=items)

def enumerated_premises(base,body,block,items):
    a,b=block
    before=body[:a].strip()
    after=body[b:].strip()
    if not INTRO.match(before) or len(items)>18 or len(items)<1 or not after:return None
    if EQUIV.search(before) or IFF.search(mask_math(after)):return None
    if not re.search(r"(?i)\b(?:assume|suppose)\s*:?\s*$",before):
        return None
    m=re.match(r"(?is)^(?:Then|It\s+follows\s+that|We\s+conclude\s+that)\s*[:.,]?\s*(.+)$",after)
    if not m:return None
    conclusion=m.group(1).strip()
    if not conclusion or PLACEHOLDER.search(conclusion):return None
    h=before+"\n"+body[a:b]
    return make(base,[h],[conclusion],"joint_enumerated_assumptions",
                "All enumerated clauses are jointly assumed; result follows after explicit Then",
                cases=[{"logical_form":"implication","hypotheses":[h],
                        "conclusions":[conclusion],"source_clause":after}])

def enumerated_conditionals(base,body,block,items):
    a,b=block
    before=body[:a].strip()
    tail=body[b:].strip(" .\n\t")
    if tail or len(items)<2 or len(items)>16:return None
    if not before or EQUIV.search(before) or IFF.search(mask_math(before)):
        return None
    if ASSUME_END.search(before) or re.search(r"(?i)\b(?:following\s+properties|conditions\s+hold)\s*:?\s*$",before):
        return None
    if not (INTRO.match(before) or re.search(r"(?i)\bthe\s+following\s+(?:hold|are\s+true)\s*:?\s*$",before)):
        return None
    if any("\\begin{enumerate}" in item for item in items):return None
    clauses=[];hypotheses=[before];conclusions=[]
    for item in items:
        s=mask_math(item)
        if IFF.search(s) or re.search(r"(?i)\bconversely\b",s):
            return None  # scoped iff + addenda need individual editorial handling
        m=IF_THEN.search(s)
        if not m or not ANY_WHEN.match(item.strip()):return None
        h=item[:m.start()].strip()
        c=item[m.end():].strip()
        if not h or not c or re.search(r"(?i)\b(?:also|moreover|in\s+this\s+case)\b",c):
            return None
        clauses.append({"logical_form":"conditional_subcase",
                        "hypotheses":[before,h],"conclusions":[c],
                        "source_clause":item})
        if h not in hypotheses:hypotheses.append(h)
        conclusions.append(c)
    return make(base,hypotheses,conclusions,"independent_source_conditional_cases",
                "Enumerated implications retain item-level hypothesis/conclusion scope",
                cases=clauses)

def enumerated_assertions(base,body,block,items):
    a,b=block
    before=body[:a].strip()
    tail=body[b:].strip(" .\n\t")
    if tail or not before or len(items)>12 or len(items)<2:return None
    if EQUIV.search(before) or IFF.search(mask_math(before)) or ASSUME_END.search(before):
        return None
    if not re.search(r"(?i)\b(?:then\s+(?:we\s+have)?|"
                     r"the\s+following\s+(?:results|hold|are\s+true)|"
                     r"we\s+have)\s*:?\s*$",before):
        return None
    if any("\\begin{enumerate}" in z or
           re.search(r"(?i)^\s*(?:Let|Suppose|Assume|Conversely)\b",z)
           for z in items):
        return None
    if not INTRO.match(before):return None
    shared=before
    cases=[logical_item(x,shared) for x in items]
    if any(x["logical_form"]=="equivalence_subcase" for x in cases):
        return None
    hs=[shared];cs=[]
    for case in cases:
        for h in case["hypotheses"][1:]:
            if h not in hs:hs.append(h)
        cs.extend(case["conclusions"])
    return make(base,hs,cs,"enumerated_explicit_results",
                "Source-introduced result list, conditional subcases kept separate",
                cases=cases)

def setup_with_assertion(base,body):
    if len(body)>1800 or "\\begin" in body:return None
    setup=safe_setup(body)
    if not setup:return None
    a,b=setup
    if not ASSERT_START.match(b) or IFF.search(mask_math(b)):return None
    if PLACEHOLDER.search(b) or MULTI_TAIL.search(b):return None
    if not re.search(r"(?i)\b(?:is|are|has|have|exists?|gives|induces|can|defines|"
                     r"commutes|satisfies|splits|agrees|equivalent|bijection)\b",mask_math(b)):
        return None
    return make(base,[a],[b],"source_setup_assertion",
                "Completed explicit source setup followed by a single assertion")

def subject_assertion(base,body):
    if len(body)>390 or "\\begin" in body or "\n\n" in body:
        return None
    if IFF.search(mask_math(body)) or PLACEHOLDER.search(body):
        return None
    if re.search(r"(?i)\b(?:then|conversely|moreover|in\s+particular)\b",mask_math(body)):
        return None
    m=SINGLE_SUBJECT.match(body.strip())
    if not m:return None
    subject=m.group("subject").strip()
    if re.search(r"(?i)\b(?:which|that|such\s+that|is|are|has|have|exists?)\b",subject):
        return None
    if len(subject)>150 or len(subject)<10:return None
    # The subject is a retrieval term, *not* an additional assertion.
    return make(base,[subject],[body],"unconditional_subject_and_assertion",
                "Source subject used for hypothesis-side search only; theorem remains unconditional")

def interpret(base):
    body,_=source_body(base["statement"])
    if not body or PLACEHOLDER.search(body) or EXTERNAL.search(body):
        return None,"editorial_placeholder_or_inherited_context"
    blocks=enum_blocks(body)
    if blocks is None:return None,"unbalanced_enumeration"
    if len(blocks)==1:
        items=list_items(body,blocks[0])
        if not items or any(PLACEHOLDER.search(x) for x in items):
            return None,"incomplete_source_list"
        for fn in (explicit_equivalence,enumerated_premises,
                   enumerated_conditionals,enumerated_assertions):
            result=fn(base,body,blocks[0],items)
            if result:return result,fn.__name__
        return None,"complex_enumerated_scope"
    if blocks:
        return None,"multiple_separate_list_scopes"
    for fn in (setup_with_assertion,subject_assertion):
        result=fn(base,body)
        if result:return result,fn.__name__
    return None,"unconditional_or_complex_statement_no_safe_search_premise"

def main():
    before_total=Counter()
    allforms=Counter()
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        original=p.load_rows(w/"pass2.jsonl","candidate_id")
        old=Counter(v["context_status"] for v in original.values())
        before_total.update(old)
        revised=[];deferred=[];forms=Counter()
        for ident,v in sorted(original.items()):
            if v["context_status"]!="needs_structure":continue
            updated,why=interpret(v)
            if updated:
                revised.append(updated);forms[why]+=1
            else:deferred.append({"candidate_id":ident,"reason":why,
                     "source_statement":v["statement"],
                     "higher_thinking_needed":True,
                     "current_status":"needs_structure"})
        if revised:
            path=w/"pass2_structural_refined_decisions.jsonl"
            p.atomic_text(path,"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in revised))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(path),replace=True))
        new=p.load_rows(w/"pass2.jsonl","candidate_id")
        statuses=Counter(v["context_status"] for v in new.values())
        assert set(original)==set(new)
        assert statuses["needs_structure"]==old["needs_structure"]-len(revised)
        assert statuses["needs_context"]==old["needs_context"]
        assert statuses["needs_classification"]==old["needs_classification"]
        assert not p.load_rows(w/"pass3.jsonl","candidate_id")
        p.atomic_text(w/"pass2_structural_refined_higher_thinking.jsonl",
                      "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in deferred))
        summary={"batch":batch,"before_structure":old["needs_structure"],
                 "new_resolved":len(revised),
                 "remaining_structure":statuses["needs_structure"],
                 "recovery_methods":dict(sorted(forms.items())),
                 "status_after":dict(sorted(statuses.items())),
                 "proofs_read":False,"published_catalog_unchanged":True}
        p.atomic_text(w/"pass2_structural_refined_summary.json",
                      json.dumps(summary,sort_keys=True,indent=2)+"\n")
        allforms.update(forms)
        print(json.dumps(summary,sort_keys=True))
    print(json.dumps({"methods_total":dict(sorted(allforms.items())),
                      "newly_resolved":sum(allforms.values()),
                      "before_total":dict(sorted(before_total.items()))},sort_keys=True))
if __name__=="__main__":main()

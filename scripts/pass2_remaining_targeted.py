#!/usr/bin/env python3
"""Targeted Pass 2 source-statement interpretation after hard_followup.

Run on the existing deferred queue only. Preserve original theorem statement,
provenance, and candidate classification. No proof text, validity check, or
catalog publication. Ambiguous logical scope remains deferred.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

try:
    from . import harvest_pipeline as pipeline
    from .pass2_hard_followup import interpret_followup, repack
    from .pass2_hard_structures import (AMBIGUOUS, CROSS_CONTEXT, INTRO,
                                          EQUIV, enum_blocks, list_items,
                                          safe_setup, mask_math, logical_item)
except ImportError:
    import harvest_pipeline as pipeline
    from pass2_hard_followup import interpret_followup, repack
    from pass2_hard_structures import (AMBIGUOUS, CROSS_CONTEXT, INTRO,
                                        EQUIV, enum_blocks, list_items,
                                        safe_setup, mask_math, logical_item)

REFPRE = re.compile(r"^\s*\\begin\{(?:reference|history)\}[\s\S]*?\\end\{(?:reference|history)\}\s*", re.I)
CONTEXT = re.compile(r"\b(?:as\s+before|as\s+above|constructions?\s+above|"
                     r"with\s+(?:the\s+)?notation\s+of|situation\s+\\ref|"
                     r"under\s+the\s+assumptions\s+of)\b", re.I)
IFANDONLY = re.compile(r"\bif\s+and\s+only\s+if\b", re.I)
EXISTS = re.compile(r"\b(?:there\s+(?:exists?|are|is)|we\s+(?:obtain|have|find)|"
                    r"there\s+is\s+a\s+canonical|one\s+(?:has|obtains))\b",re.I)
ALTERNATE = re.compile(r"\bin\s+each\s+of\s+the\s+following\s+cases\b",re.I)


def source_body(source):
    body=source.strip()
    removed=False
    while True:
        m=REFPRE.match(body)
        if not m: break
        body=body[m.end():].strip()
        removed=True
    return body,removed


def make(base,h,c,form,reason,*,equivalence=None,cases=None):
    if not h or not c or any(not str(v).strip() for v in h+c):
        return None
    return {
        **base,"hypotheses":h,"conclusions":c,
        "logical_form":form,
        "equivalence_sides":[[v] for v in equivalence] if equivalence else [],
        "structured_cases":cases or [],
        "context_status":"resolved","context_note":"",
        "split_confidence":"bounded_source_interpretation_unverified",
        "review_method":"editorial",
        "statement_editorial_notes":"Bounded Pass 2 source-only interpretation: "+reason+
                                    ". Original source and context retained; no proof reviewed.",
    }


def equivalent_with_context(base,body):
    """Only literal top-level iff (one occurrence); never create multiple results."""
    masked=mask_math(body)
    hits=list(IFANDONLY.finditer(masked))
    if len(hits)!=1 or "\\begin{enumerate}" in body:
        return None
    m=hits[0]
    hbody=body[:m.start()].strip()
    right=body[m.end():].strip()
    if not hbody or not right:
        return None
    # Distinguish common setup sentences from equivalence's left condition.
    setup=""
    left=hbody
    intro=safe_setup(hbody)
    if intro:
        setup,left=intro
    if re.search(r"\b(?:in\s+particular|moreover|furthermore|also)\b",right,re.I):
        return None
    if re.search(r"\b(?:then|conversely)\b",left,re.I):
        return None
    if left.endswith(":") or left.lower().endswith("if"):
        return None
    sides=[left,right]
    cases=[{"logical_form":"equivalence","hypotheses":sides,
            "conclusions":sides,"source_clause":body}]
    return make(base,([setup] if setup else [])+sides,list(sides),
                "equivalence","One explicit iff; each side searchable as both hypothesis and conclusion",
                equivalence=sides,cases=cases)


def assume_list_then(base,body,blocks):
    """If initial source enum lists premises, conclusion is text after Then."""
    if len(blocks)!=1: return None
    a,b=blocks[0]
    pre=body[:a].strip()
    tail=body[b:].strip()
    if not re.search(r"\b(?:assume|suppose|given)\s*:?\s*$",pre,re.I):
        return None
    m=re.match(r"^(?:Then|It\s+follows\s+that)\b[\s,.:]*(.+)$",tail,re.S|re.I)
    items=list_items(body,blocks[0])
    if not m or not items or not INTRO.match(pre):
        return None
    setup=pre+"\n"+body[a:b]
    claim=m.group(1).strip()
    if not claim:return None
    if IFANDONLY.search(mask_math(claim)):
        iff=IFANDONLY.search(mask_math(claim))
        lhs,rhs=claim[:iff.start()].strip(),claim[iff.end():].strip()
        if lhs and rhs and not IFANDONLY.search(rhs):
            return make(base,[setup,lhs,rhs],[lhs,rhs],
                        "equivalence_with_enumerated_premises",
                        "Explicit listed standing assumptions and biconditional result",
                        equivalence=[lhs,rhs],
                        cases=[{"logical_form":"equivalence",
                                "hypotheses":[setup,lhs,rhs],
                                "conclusions":[lhs,rhs],"source_clause":claim}])
        return None
    return make(base,[setup],[claim],"implication_with_enumerated_premises",
                "Explicit list of standing assumptions followed by Then",
                cases=[{"hypotheses":[setup],"conclusions":[claim],
                        "source_clause":tail,"logical_form":"implication"}])


def alternate_sufficient(base,body,blocks):
    """In each following cases, RESULT: [assumptions]."""
    if len(blocks)!=1:return None
    a,b=blocks[0]
    pre=body[:a].strip()
    after=body[b:].strip()
    if after: return None
    m=ALTERNATE.search(pre)
    if not m:return None
    items=list_items(body,blocks[0])
    if not items or len(items)>12: return None
    context=pre[:m.start()].strip()
    claim=pre[m.end():].strip(" :\n")
    if not claim or not re.search(r"\b(?:is|are|has|have|admits|can|exists?|defined)\b",mask_math(claim),re.I):
        return None
    if AMBIGUOUS.search(body):return None
    cases=[{"hypotheses":[context,item] if context else [item],
            "conclusions":[claim],"source_clause":item,
            "logical_form":"alternative_sufficient_condition"} for item in items]
    h=([context] if context else [])+items
    return make(base,h,[claim],"alternative_sufficient_conditions",
                "Each explicitly listed case independently suffices for the stated result",
                cases=cases)


def explicit_existential(base,body):
    """Bounded setup followed by explicit quantifier 'there exists'."""
    if len(body)>1150 or "\\begin{enumerate}" in body:return None
    m=EXISTS.search(mask_math(body))
    if not m or m.start()<15 or not INTRO.match(body):return None
    setup=body[:m.start()].strip()
    claim=body[m.start():].strip()
    if not setup or not claim:return None
    # Avoid assigning a condition already introducing the quantified object
    # to a wholly unrelated premise.
    if setup.lower().endswith(("if","that","such that","when","and","or","as")):
        return None
    if re.search(r"\b(?:then|if\s+and\s+only\s+if)\b",setup,re.I):
        return None
    return make(base,[setup],[claim],"source_setup_existential",
                "Explicit setup clause preceding existential assertion")


def universal_source_subject(base,body):
    """Source subject indexing, not fabricated one-way implications."""
    if not body or len(body)>530 or "\\begin{" in body or "\n\n" in body:return None
    if IFANDONLY.search(body) or re.search(r"\b(?:if|provided|unless|whenever)\b",mask_math(body),re.I):
        return None
    if re.search(r"\b(?:as\s+above|in\s+lemma|in\s+example|situation)\b",body,re.I):
        return None
    # Whole assertion is the conclusion. The beginning is a subject for
    # retrieval, not a mathematically independent premise.
    m=re.match(r"^((?:The|A|An|Any|Every|Each|All)\s+.{6,210}?)\s+"
        r"(?:is|are|has|have|admits|defines|commutes|satisfies)\s+"
        r"\S",body,re.I|re.S)
    if not m:return None
    subject=m.group(1).strip()
    if re.search(r"\b(?:which|such\s+that)\b",subject,re.I):
        return None
    return make(base,[subject],[body],"source_subject_and_assertion",
                "Unconditional source subject tagged as searchable context; full assertion retained")


def interpret_targeted(base):
    original=base["statement"].strip()
    body,removed=source_body(original)
    if not body or CONTEXT.search(body) or AMBIGUOUS.search(body) or CROSS_CONTEXT.search(body):
        return None,"Missing context or incomplete source text"
    # First retry source-grammar with citation/history header removed.
    if removed:
        parsed,reason=interpret_followup({**base,"statement":body})
        if parsed:
            return make(base,parsed["hypotheses"],parsed["conclusions"],
                        parsed["logical_form"],"Source metadata preface excluded from logical statement; "+reason if reason else "Citation preface excluded",
                        equivalence=[s[0] for s in parsed.get("equivalence_sides",[]) if len(s)==1],
                        cases=parsed.get("structured_cases",[])),"handled"
    blocks=enum_blocks(body)
    if blocks is None:return None,"Unbalanced list environment"
    if blocks:
        for fn in (assume_list_then,alternate_sufficient):
            result=fn(base,body,blocks)
            if result:return result,"handled"
        return None,"Complex enumerations or additional conclusions still require review"
    for fn in (equivalent_with_context,explicit_existential,universal_source_subject):
        result=fn(base,body)
        if result:return result,"handled"
    return None,"Requires actual editorial interpretation; source boundary not safely identified"


def run(args):
    w=Path(args.workdir)
    queue=pipeline.load_rows(w/"pass2_higher_thinking_remaining_v2.jsonl","candidate_id")
    before=pipeline.load_rows(w/"pass2.jsonl","candidate_id")
    updates,still=[],[]
    forms=Counter()
    for ident,q in sorted(queue.items()):
        current=before.get(ident)
        if not current or current["context_status"]!="needs_structure":
            raise ValueError(f"{ident}: no longer unresolved in canonical Pass 2")
        item,reason=interpret_targeted(current)
        if item:
            updates.append(item)
            forms[item["logical_form"]]+=1
        else:
            still.append({**q,"reason_after_targeted_review":reason})
    if updates:
        target=w/"pass2_targeted_decisions.jsonl"
        pipeline.atomic_text(target,"".join(json.dumps(v,ensure_ascii=False,sort_keys=True)+"\n" for v in updates))
        pipeline.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(target),replace=True))
    pipeline.atomic_text(w/"pass2_higher_thinking_remaining_v3.jsonl",
        "".join(json.dumps(v,ensure_ascii=False,sort_keys=True)+"\n" for v in still))
    final=pipeline.load_rows(w/"pass2.jsonl","candidate_id")
    status=Counter(x["context_status"] for x in final.values())
    report={
        "stage":"pass2_targeted_statement_review",
        "started_from":len(queue),"newly_resolved":len(updates),
        "structurally_unresolved":len(still),
        "new_forms":dict(sorted(forms.items())),
        "statuses":dict(sorted(status.items())),
        "proofs_read":False,"mathematical_validity_assessed":False,
    }
    assert len(queue)==len(updates)+len(still)
    pipeline.atomic_text(w/"pass2_targeted_summary.json",json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,sort_keys=True))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--workdir",required=True)
    run(parser.parse_args())

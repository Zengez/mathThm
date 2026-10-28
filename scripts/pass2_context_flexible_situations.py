#!/usr/bin/env python3
"""Resolve further Pass 2 named-Situation contexts embedded within Let statements.

Only original cited Situation LaTeX statement is copied. Logical boundaries are
source-explicit (Then, if-then, source equivalence, enumerated conditional cases).
No definitions inferred, proof analysis, mathematics verification or publication.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from collections import Counter

try:
    from . import harvest_pipeline as p
    from .pass2_context_source_probe import get_index,BATCHES
    from .pass2_remaining_targeted import source_body
    from .pass2_context_expansion import split_source,prepare
    from .pass2_hard_structures import (interpret as interpret_hard,
        mask_math,enum_blocks,list_items,logical_item)
    from .pass2_hard_followup import interpret_followup
except ImportError:
    import harvest_pipeline as p
    from pass2_context_source_probe import get_index,BATCHES
    from pass2_remaining_targeted import source_body
    from pass2_context_expansion import split_source,prepare
    from pass2_hard_structures import (interpret as interpret_hard,
        mask_math,enum_blocks,list_items,logical_item)
    from pass2_hard_followup import interpret_followup

REF=re.compile(
    r"\b(?:In|Under|as\s+in|from|of)\s+(?:the\s+)?Situation\s*"
    r"\\ref\{(?P<label>situation-[^{}]+)\}",re.I)
INTRO=re.compile(r"^(?:Let|In|Under|Assume|Suppose|Given|Notation|With)\b",re.I)
THEN=re.compile(r"\bthen\b",re.I)
EQUIV=re.compile(r"\b(?:are|is)\s+equivalent\b",re.I)
REMAINDER_CONTEXT=re.compile(r"(?i)\b(?:with\s+notation\s+as\s+(?:above|in)|"
                            r"as\s+before|as\s+above|in\s+the\s+situation\s+above|"
                            r"assumptions\s+and\s+notation\s+as\s+in\s+Lemma)\b")

def from_source(original):
    body,_=source_body(original)
    return body

def boundaries(body):
    # Explicit condition/result divide. Prefer prior reviewed grammatical
    # interpreters that retain equivalence and structured-case provenance.
    for fn in (interpret_followup,interpret_hard):
        try:
            v,_=fn({"statement":body})
            if v and v.get("hypotheses") and v.get("conclusions"):
                return v,"source logical-form parser"
        except (KeyError,ValueError,TypeError,IndexError):
            pass
    plain=mask_math(body)
    blocks=enum_blocks(body)
    if blocks is None:return None,"unbalanced list structure"
    for m in THEN.finditer(plain):
        if any(a<=m.start()<b for a,b in blocks):continue
        h,c=body[:m.start()].strip(),body[m.end():].strip()
        if not h or not c or not INTRO.match(h):continue
        if EQUIV.search(body[:m.start()]) or EQUIV.search(body[m.end():]):
            # A theorem-level biconditional needs the explicit bidirectional
            # parser, not flattening into one-way 'Then'.
            continue
        if h.endswith(("and","or","such that","if","that")):
            continue
        return {"hypotheses":[h],"conclusions":[c],
            "logical_form":"source_explicit_then_with_named_situation",
            "equivalence_sides":[],"structured_cases":[]}, "top-level Then after standing assumptions"
    # Standalone source enumeration of conditional consequences under the
    # recovered Situation, even if no further Let/Assume prefix appears.
    if len(blocks)==1:
        a,b=blocks[0]
        before=body[:a].strip()
        after=body[b:].strip()
        items=list_items(body,blocks[0])
        if not after and items and len(items)<=16 and not EQUIV.search(before):
            if not re.search(r"(?i)\b(?:assume|suppose|given)\s*:?\s*$",before):
                cases=[logical_item(z,before) for z in items]
                if all(c["logical_form"] in ("conditional_subcase","equivalence_subcase") for c in cases):
                    h=[before]
                    c=[]
                    for item in cases:
                        h.extend(x for x in item["hypotheses"][1:] if x not in h)
                        c.extend(item["conclusions"])
                    return {"hypotheses":h,"conclusions":c,
                        "logical_form":"source_enumerated_conditional_situation",
                        "equivalence_sides":[],"structured_cases":cases},"Explicit conditional clauses within Situation"
    return None,"statement still requires contextual editorial interpretation"

def interpret(base,raw,index):
    full=base["statement"]
    body=from_source(full)
    if not INTRO.match(body):return None,"no source Situation setup"
    match=REF.search(body[:450])
    if not match:return None,"no early direct Situation reference"
    name=match.group("label")
    file=raw["source"]["filename"]
    info=index.get((file,name))
    if not info or info["kind"] not in ("situation","setup","notation"):
        return None,"named Situation not present in pinned source file"
    if len(info["text"])<25 or len(info["text"])>2700:
        return None,"named Situation context length outside permitted range"
    if re.search(r"\\ref\{(?:situation|setup)-[^{}]+\}",info["text"]):
        return None,"Situation itself has inherited Situation dependencies"
    if REMAINDER_CONTEXT.search(body):
        return None,"separate external assumptions may also be required"
    out,why=boundaries(body)
    if not out:return None,why
    # Pass the original theorem text, not the full source or relabeled
    # hypothesis, to the canonical Pass 2 record.
    result=prepare(base,info,name,file,raw["source"]["revision"],body,out,why)
    result["split_confidence"]="pinned_situation_flexible_source_interpretation_unverified"
    result["statement_editorial_notes"]=(
        "Flexible named Situation Pass 2 source lookup. "+why+
        "; preserved original statement. No mathematical validation or proof reading."
    )
    return result,"source_situation_expanded"

def run(args):
    root=Path(args.source_root)
    data={}
    allfiles=set()
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        raw=p.load_rows(w/"pass1.jsonl","candidate_id")
        current=p.load_rows(w/"pass2.jsonl","candidate_id")
        data[batch]=(w,raw,current)
        allfiles.update(v["source"]["filename"] for v in raw.values())
    idx=get_index(root,allfiles)
    for batch,(w,raw,current) in data.items():
        updated=[];reasons=Counter()
        for ident,item in sorted(current.items()):
            if item["context_status"]!="needs_context":continue
            out,why=interpret(item,raw[ident],idx)
            if out: updated.append(out)
            else: reasons[why]+=1
        if updated:
            path=w/"pass2_context_flexible_situations_decisions.jsonl"
            p.atomic_text(path,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in updated))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(path),replace=True))
        final=p.load_rows(w/"pass2.jsonl","candidate_id")
        summary={"newly_resolved":len(updated),
            "initial_context_pending":sum(v["context_status"]=="needs_context" for v in current.values()),
            "statuses":dict(sorted(Counter(v["context_status"] for v in final.values()).items())),
            "deferred_reasons":dict(sorted(reasons.items())),
            "source_revision":"a04446e57ec1fbc252a871afcec7752fb2807b14",
            "proofs_read":False,"mathematical_validity_assessed":False}
        p.atomic_text(w/"pass2_context_flexible_situations_summary.json",json.dumps(summary,indent=2,sort_keys=True)+"\n")
        print(json.dumps({"batch":batch,**summary},sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",default="upstream/stacks")
    run(ap.parse_args())

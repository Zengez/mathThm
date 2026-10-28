#!/usr/bin/env python3
"""Fifth bounded Pass 2 statement/source-context review of unresolved Stacks.

Resolve precisely located SAME-FILE lemma/proposition/theorem references that
have explicit source-native grammatical hypotheses/conclusions. Keep the
referenced source statement for audit, not its proof. Theorems using outside
chapters, ambiguous references, or editorial placeholders stay open.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path
from . import harvest_pipeline as p
from .pass2_context_source_probe import get_index, BATCHES
from .pass2_remaining_targeted import source_body
from .pass2_hard_structures import mask_math, enum_blocks, list_items, AMBIGUOUS
from .pass2_hard_structures import safe_setup
from .pass2_context_secondary import parse_statement

NAMED=re.compile(
    r"\b(?:as\s+in|from|of|in\s+the\s+(?:situation|setting)\s+of|"
    r"with\s+(?:the\s+)?(?:notation|assumptions)\s+of)\s+"
    r"(?:[A-Z][A-Za-z ]{0,50},\s*)?"
    r"(?:Lemma|Proposition|Theorem)\s*\\ref\{(?P<label>[^{}]+)\}",
    re.I,
)
EQUIVALENCE=re.compile(
    r"\b(?:the\s+following|following\s+conditions|these\s+conditions)\s+"
    r"(?:are|is)\s+equivalent\b",re.I,
)
IFF=re.compile(r"\bif\s+and\s+only\s+if\b",re.I)
CONTEXT_INTRO=re.compile(r"^(?:Let|Suppose|Assume|Consider|Given|With|In|Under|Fix|For)\b",re.I)
UNSAFE=re.compile(r"\b(?:as\s+above|in\s+the\s+situation\s+above|"
    r"with\s+notation\s+as\s+above|we\s+should\s+prove|"
    r"add\s+more\s+here|to\s+do)\b",re.I)

def named_labeled_refs(body):
    return [(x.group("label"),x.start(),x.end()) for x in NAMED.finditer(body)]

def extract_setup_from_reference(source):
    """Returning actual text not paraphrase, never importing lemma conclusion."""
    text=source["text"].strip()
    if not CONTEXT_INTRO.match(text) or len(text)>2300:return None
    explicit=safe_setup(text)
    if explicit:
        return explicit[0]
    masked=mask_math(text)
    candidates=[m for m in re.finditer(r"\bthen\b",masked,re.I)]
    blocks=enum_blocks(text)
    if blocks is None:return None
    for m in candidates:
        if any(a<=m.start()<b for a,b in blocks):continue
        head=text[:m.start()].strip()
        if head and CONTEXT_INTRO.match(head):
            return head
    # Intro-only source paragraphs followed by an explicit existence statement.
    m=re.search(r"\.\s+(?=(?:There|The|For)\b)",masked)
    if m:
        h=text[:m.end()].strip()
        if h and CONTEXT_INTRO.match(h):return h
    return None

def source_grammar(body):
    """Returns grammatical index fields with source clauses preserved."""
    if not body or AMBIGUOUS.search(body) or UNSAFE.search(body):
        return None,"Unfinished or explicitly unresolved prior-context source"
    blocks=enum_blocks(body)
    if blocks is None:return None,"Malformed enumerations"
    masked=mask_math(body)
    # Explicit equivalence: all enumerated conditions searched bidirectionally.
    if len(blocks)==1:
        a,b=blocks[0]
        m=EQUIVALENCE.search(body[:a])
        items=list_items(body,blocks[0])
        tail=body[b:].strip(" \n\t.")
        if m and items and 2<=len(items)<=16 and not tail and CONTEXT_INTRO.match(body[:m.start()]):
            leading=body[:m.start()].strip()
            if body[m.end():a].strip(" \n\t.:")=="":
                return {"hypotheses":[leading]+items,"conclusions":list(items),
                        "logical_form":"pinned_named_reference_equivalence",
                        "equivalence_sides":[[item] for item in items],
                        "structured_cases":[]}, "Explicit enumerated equivalence"
    # Source-grammatical Then, except that embedded iff must retain both sides.
    if not CONTEXT_INTRO.match(body):return None,"No explicit main setup"
    thens=[m for m in re.finditer(r"\bthen\b",masked,re.I)
           if not any(a<=m.start()<b for a,b in blocks)]
    if len(thens)!=1:
        # A simple source intro plus separate existence assertion is safe.
        setup=safe_setup(body)
        if setup:
            h,c=setup
            if re.match(r"^There\s+(?:is|are|exist|exists)\b",c,re.I) and IFF.search(masked) is None:
                return {"hypotheses":[h],"conclusions":[c],
                    "logical_form":"pinned_named_reference_existential",
                    "equivalence_sides":[],"structured_cases":[]}, "Named reference with source setup and existential assertion"
        return None,"Ambiguous or absent top-level Then"
    m=thens[0]
    head,claim=body[:m.start()].strip(),body[m.end():].strip()
    if not head or not claim or head.endswith(("if","or","and","such that")):
        return None,"Incomplete premise or conclusion"
    if re.search(r"\b(?:assume|suppose|given)\s*:?\s*$",head,re.I) and not blocks:
        return None,"Premise list marker with no enumerated assumptions"
    if IFF.search(mask_math(claim)):
        iff=list(IFF.finditer(mask_math(claim)))
        if len(iff)!=1 or blocks:return None,"Complex implication containing biconditional"
        ix=iff[0]
        left,right=claim[:ix.start()].strip(),claim[ix.end():].strip()
        if not left or not right:return None,"Incomplete biconditional"
        # Source says standing assumptions => (P iff Q), so both search fields
        # carry P,Q. A single canonical theorem and explicit shared assumptions.
        return {"hypotheses":[head,left,right],
                "conclusions":[left,right],
                "logical_form":"pinned_named_reference_conditional_equivalence",
                "equivalence_sides":[[left],[right]],
                "structured_cases":[{"logical_form":"equivalence","hypotheses":[head,left,right],
                                     "conclusions":[left,right],"source_clause":claim}]},
                "Explicit biconditional consequence of named context"
    if IFF.search(masked):
        return None,"Theorem involves iff outside the asserted result"
    return {"hypotheses":[head],"conclusions":[claim],
            "logical_form":"pinned_named_reference_implication",
            "equivalence_sides":[],"structured_cases":[]}, "Source explicit top-level Then"

def interpret(base,raw,index):
    body,_=source_body(base["statement"])
    matches=named_labeled_refs(body)
    if not matches:return None,"No named lemma/proposition/theorem reference"
    fn=raw["source"]["filename"]
    line=raw["source"]["statement_line"]
    refs=[]
    for label,start,end in matches:
        entry=index.get((fn,label))
        if not entry:
            return None,"Reference unavailable in same source file"
        if entry["kind"] not in ("lemma","theorem","proposition"):
            return None,"Referenced source entity is not an assertion"
        if entry["line"]>=line:
            return None,"Reference does not point to earlier source statement"
        if len(entry["text"])>2600:
            return None,"Referenced source statement too long for bounded expansion"
        refs.append((label,entry))
    if len(refs)>2:
        return None,"More than two named lemma references"
    parsed,why=source_grammar(body)
    if parsed is None:
        return None,why
    if not parsed["hypotheses"] or not parsed["conclusions"]:
        return None,"Missing one searchable side"
    extracted=[]
    for label,entry in refs:
        setup=extract_setup_from_reference(entry)
        extracted.append({"label":label,"kind":entry["kind"],
                          "filename":fn,"statement_line":entry["line"],
                          "source_revision":raw["source"]["revision"],
                          "source_statement":entry["text"],
                          "inherited_setup":setup})
    # The original source setup carries the reference itself. Do not treat
    # a previous lemma's mathematical RESULT as an assumption. Keep its
    # exact source separately for interpreting the referenced notation.
    return {**base,**parsed,
            "context_status":"resolved","context_note":"",
            "review_method":"editorial",
            "split_confidence":"pinned_local_reference_source_grammar_unverified",
            "local_context_used":extracted,
            "statement_editorial_notes":"Pass 2: "+why+
                ". Named same-file reference source statements recovered at exact pinned revision; "+
                "source statement retained; no proof reading or mathematical verification.",
           },"resolved"

def run(args):
    root=Path(args.source_root)
    batches={}
    allfiles=set()
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        raw=p.load_rows(w/"pass1.jsonl","candidate_id")
        rows=p.load_rows(w/"pass2.jsonl","candidate_id")
        batches[batch]=(w,raw,rows)
        allfiles.update(x["source"]["filename"] for x in raw.values())
    index=get_index(root,allfiles)
    for name,(w,raw,rows) in batches.items():
        changed=[];blocked=Counter();forms=Counter()
        for ident,row in sorted(rows.items()):
            if row["context_status"]!="needs_context":continue
            entry,reason=interpret(row,raw[ident],index)
            if entry:
                changed.append(entry);forms[entry["logical_form"]]+=1
            else:blocked[reason]+=1
        if changed:
            filename=w/"pass2_pinned_named_reference_decisions.jsonl"
            p.atomic_text(filename,"".join(json.dumps(d,ensure_ascii=False,sort_keys=True)+"\n" for d in changed))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(filename),replace=True))
        final=p.load_rows(w/"pass2.jsonl","candidate_id")
        summary={"batch":name,"previous_context_open":sum(x["context_status"]=="needs_context" for x in rows.values()),
                 "new_resolved":len(changed),"by_logical_form":dict(sorted(forms.items())),
                 "not_resolved_reasons":dict(sorted(blocked.items())),
                 "current_states":dict(sorted(Counter(x["context_status"] for x in final.values()).items())),
                 "proofs_read":False,"mathematical_validity_assessed":False}
        p.atomic_text(w/"pass2_pinned_named_reference_summary.json",json.dumps(summary,indent=2,sort_keys=True)+"\n")
        print(json.dumps(summary,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",default="upstream/stacks")
    run(ap.parse_args())

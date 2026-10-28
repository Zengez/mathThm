#!/usr/bin/env python3
"""Statement-level Pass 2 QC of explicit editorial splits just applied.

Only source text and source-derived clause structures are inspected; no
proof, theorem validation, or publication. Correct two-valuative-criterion
closure antecedents and one conjunction-valued equivalence, improve two
parallel G-unramified cases and one implicit If/so clause, and requeue
seven incomplete or locally scoped enumerated cases.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from . import harvest_pipeline as p
from .pass2_hard_structures import enum_blocks,list_items,mask_math

BULK="stacks-bulk-2026-10-28"
REMAINING="stacks-remaining-2026-10-28"
DEFERRED={
    "08efbb85d6b3a2ef6338aa1a": "Graph classification: 'are given by' item has no independent subject",
    "9d203baef6d4c95fe167a218": "Graph classification: item is grammatically dependent on a preceding object list",
    "af81928d74171374eae907a9": "Graph classification: fragmentary enumerated form under diagram context",
    "cfe7c73282c96bae1f3c2194": "Graph classification: fragmentary matrix specification after source setup",
    "d4960d49befe0d0f4fff0978": "Alternative graph configurations need scope-aware formulation",
    "f4731c1d4e806aec343ee958": "Second enumerated clause depends on first clause's own diagram setup",
    "6a8fa4526dbae5f161c09909": "Second enumerated result has additional local assumptions not separately indexed",
}
COMPOSITES={
    "2e723b746c1cd7c584d724d6",
    "dce08e840cd16fee619803f6",
}
PARALLEL={
    "021448cd1d63bc67c087d3a0",
    "51659105a8072cb00d2d9c76",
}
EQUIV="e1cf0ed4b026a8844d7b889c"
IMPLICIT_IF="063628acbfbbb1201c26f138"

def key(s):
    return "candidate.stacks."+s

def requeue(row,reason):
    return {**row,
        "hypotheses":[],"conclusions":[],
        "logical_form":"needs_structural_editorial_review",
        "equivalence_sides":[],"structured_cases":[],
        "context_status":"needs_structure",
        "context_note":"Pass 2 QC reverted over-eager semantic indexing. "+reason,
        "split_confidence":"deferred_after_statement_semantics_qc",
        "statement_editorial_notes":"Not a completed Pass 2 split: "+reason+
             ". Original source unchanged; no proof reviewed."}

def repair_composite(row):
    text=row["statement"].strip()
    match=re.match(
        r"^The composition of (?P<subject>[\s\S]+?)\s+is another\s+"
        r"morphism of algebraic stacks which satisfies[\s\S]+$",
        text,
    )
    if not match:return None
    h=match.group("subject").strip()
    if not h or not re.search(r"\bsatisfy\b",h):return None
    return {**row,
       "hypotheses":[h],
       "conclusions":[text],
       "context_status":"resolved","context_note":"",
       "logical_form":"source_closure_property",
       "structured_cases":[{"logical_form":"closure_source_assertion",
                            "hypotheses":[h],"conclusions":[text],
                            "source_clause":text}],
       "equivalence_sides":[],
       "split_confidence":"source_semantic_qc_corrected_unverified",
       "statement_editorial_notes":"Pass 2 corrected source subject to end before 'is another morphism', preserving criterion as assumption. Original source retained; no proof read."}

def repair_iff(row):
    text=row["statement"].strip()
    blocks=enum_blocks(text)
    if blocks is None or len(blocks)!=1:return None
    a,b=blocks[0]
    ix=re.search(r"\bif\s+and\s+only\s+if\b",mask_math(text[:a]),re.I)
    then=re.search(r"\bThen\b",mask_math(text[:a]),re.I)
    items=list_items(text,blocks[0])
    if not then or not ix or not items or len(items)!=2 or text[b:].strip():return None
    setup=text[:then.start()].strip()
    left=text[then.end():ix.start()].strip()
    between=text[ix.end():a].strip()
    if not re.match(r"^the two following conditions hold\s*:$",between,re.I):
        return None
    # Q is a CONJUNCTION of the two listed conditions, not each condition
    # separately equivalent to P. This is crucial for sound search indexing.
    right="Both of the following conditions hold:\n"+text[a:b]
    cases=[{"logical_form":"equivalence_with_conjunctive_side",
            "hypotheses":[setup,left,right],
            "conclusions":[left,right],
            "source_clause":text[then.start():]}]
    return {**row,"hypotheses":[setup,left,right],"conclusions":[left,right],
            "equivalence_sides":[[left],[right]],
            "structured_cases":cases,
            "logical_form":"equivalence_with_conjunctive_side",
            "context_status":"resolved","context_note":"",
            "split_confidence":"explicit_conjunction_equivalence_editorial_unverified",
            "statement_editorial_notes":"Pass 2 editorial QC: two listed conditions are JOINTLY equivalent to K being perfect; not each independently equivalent. Original source retained; no proof inspected."}

def repair_parallel(row):
    s=row["statement"]
    h=list(row["hypotheses"])
    if len(h)!=2 or "G-unramified" not in s:return None
    h[1]="G-unramified morphisms"
    cases=list(row["structured_cases"])
    if len(cases)!=2:return None
    second=dict(cases[1])
    second["hypotheses"]=[h[1]]
    cases[1]=second
    return {**row,"hypotheses":h,"structured_cases":cases,
            "split_confidence":"source_semantic_qc_corrected_unverified",
            "statement_editorial_notes":"Pass 2 QC: G-unramified morphisms are the source second-case subject; 'The same holds' is a conclusion, not a fabricated assumption."}

def repair_implicit_if(row):
    text=row["statement"]
    shared=row["hypotheses"][0]
    sections=list(row["structured_cases"])
    if len(sections)!=4:return None
    first=dict(sections[0])
    antecedent="If $S$ is geometrically reduced over $k$"
    consequent="Every $k$-subalgebra of $S$ is geometrically reduced."
    if "geometrically reduced" not in first["source_clause"]:
        return None
    first["hypotheses"]=[shared,antecedent]
    first["conclusions"]=[consequent]
    first["logical_form"]="conditional_subcase"
    first["clause_is_conditional"]=True
    sections[0]=first
    h=list(row["hypotheses"])
    if antecedent not in h:h.append(antecedent)
    c=list(row["conclusions"])
    c[0]=consequent
    return {**row,"hypotheses":h,"conclusions":c,
            "structured_cases":sections,
            "split_confidence":"source_semantic_qc_corrected_unverified",
            "statement_editorial_notes":"Pass 2 QC: explicit conditional 'If S is geometrically reduced, so is every k-subalgebra' indexed as antecedent/consequence. Original source clause retained and paraphrase marked editorial; no proof inspected."}

def run():
    targets={BULK:{IMPLICIT_IF},REMAINING:set(DEFERRED)|COMPOSITES|PARALLEL|{EQUIV}}
    totals={"requeued":0,"corrected":0}
    for batch,ids in targets.items():
        w=Path("harvest/batches")/batch
        existing=p.load_rows(w/"pass2.jsonl","candidate_id")
        changes=[]
        for short in sorted(ids):
            ident=key(short)
            current=existing[ident]
            if current["context_status"]!="resolved":
                # Already QC-reviewed on replay; don't overwrite later editorial work.
                if short in DEFERRED and current["context_status"]=="needs_structure":
                    continue
                raise ValueError(f"Unexpected status {ident}: {current['context_status']}")
            if short in DEFERRED:
                changed=requeue(current,DEFERRED[short])
                totals["requeued"]+=1
            elif short in COMPOSITES:
                changed=repair_composite(current)
                totals["corrected"]+=1
            elif short in PARALLEL:
                changed=repair_parallel(current)
                totals["corrected"]+=1
            elif short==EQUIV:
                changed=repair_iff(current)
                totals["corrected"]+=1
            else:
                changed=repair_implicit_if(current)
                totals["corrected"]+=1
            if changed is None:
                raise ValueError(f"Could not safely QC-correct {ident}")
            changes.append(changed)
        if changes:
            path=w/"pass2_semantic_qc_decisions.jsonl"
            p.atomic_text(path,"".join(json.dumps(v,sort_keys=True,ensure_ascii=False)+"\n" for v in changes))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(path),replace=True))
        print(json.dumps({"batch":batch,"changed":len(changes)}))
    assert totals=={"requeued":7,"corrected":6},totals
    print(json.dumps(totals))
if __name__=="__main__":run()

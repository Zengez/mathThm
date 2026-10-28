#!/usr/bin/env python3
"""Last bounded source-only Pass 2 structural pass: elementary plain assertions.

No proof reads, no invented premises. A source noun phrase in the 'hypotheses'
search field of an unconditional result is labeled as retrieval context, NOT
a mathematical condition. Genuinely premise-free existential theorems remain
open under the current schema; no fake hypothesis is manufactured.
"""
from __future__ import annotations
import argparse,json,re
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.pass2_context_source_probe import BATCHES
from scripts.pass2_structural_refined import make,PLACEHOLDER,EXTERNAL,IFF
from scripts.pass2_hard_structures import mask_math
from scripts.pass2_remaining_targeted import source_body

INTRO=re.compile(r"(?i)^(?:Let|Suppose|Assume|Fix|Consider|Take|Set)\b")
ASSERT=re.compile(r"(?i)^(?!(?:Let|Suppose|Assume|Fix|Consider|Take|Set)\b)"
                  r"(?:The|An?|Every|Any|All|Each|Points|Kernels|Cokernels|"
                  r"Morphisms|Homomorphisms|Functors|This|There|We)\b")
HAS_PRED=re.compile(r"(?i)\b(?:is|are|has|have|admits|exists?|define|defines|"
                    r"induce|induces|commute|commutes|agree|agrees|"
                    r"gives?|splits?|satisfy|satisfies|can|there|unique)\b")
SIMPLE_NOUN=re.compile(r"(?i)^(?:The|Every|All|Each|Any)\b")
VERB=re.compile(r"(?i)\b(?:define|defines|induce|induces|agree|agrees|"
                r"commute|commutes|transform|transforms|determine|determines|"
                r"splits?|satisfy|satisfies|"
                r"give|gives|form|forms|turn|turns)\b")
PROHIBIT=re.compile(r"(?i)\b(?:conversely|moreover|in\s+particular|"
                    r"if|whenever|provided|only\s+if)\b")

def plain_setup(base,body):
    if not INTRO.match(body) or len(body)>1350 or "\\begin" in body:
        return None
    masked=mask_math(body)
    boundaries=list(re.finditer(r"\.\s+(?=[A-Z])",masked))
    if not boundaries:return None
    for m in boundaries:
        h=body[:m.end()].strip()
        c=body[m.end():].strip()
        if not h or not c or not ASSERT.match(c) or PROHIBIT.search(mask_math(c)):
            continue
        # Check that every preceding completed source sentence is actual
        # setup, not an earlier mathematical consequence.
        earlier=re.split(r"\.\s+(?=[A-Z])",mask_math(h))
        if not earlier or any(not INTRO.match(chunk.strip()) for chunk in earlier if chunk.strip()):
            continue
        if not HAS_PRED.search(mask_math(c)):continue
        if PLACEHOLDER.search(c):continue
        return make(base,[h],[c],"source_plain_setup_assertion",
            "Source Let/Assume declarations followed by one asserted result")
    return None

def plain_subject(base,body):
    if len(body)>510 or "\\begin" in body or not SIMPLE_NOUN.match(body):
        return None
    if PROHIBIT.search(mask_math(body)) or PLACEHOLDER.search(body):
        return None
    text=mask_math(body)
    for m in VERB.finditer(text):
        h=body[:m.start()].strip()
        if len(h)<12 or len(h)>275:continue
        # The source noun-phrase is the retrieval context. It is not an
        # independently required condition. Never split at verbs in a
        # relative clause or before the object.
        if re.search(r"(?i)\b(?:which|that|where|such\s+that|"
                     r"these|when|if)\b",mask_math(h)):
            continue
        if not re.search(r"\w",body[m.end():]):continue
        return make(base,[h],[body],
             "source_subject_unconditional_assertion",
             "Source subject used as search-side context; full unconditional result retained")
    # Intransitive predicate: e.g. 'Every exact sequence ... splits.'
    m=re.match(r"(?is)^(?P<context>(?:Every|Any|Each|All|The)\s+.{10,225}?)"
       r"\s+(?:splits|commutes|exists)\s*\.?$",body.strip())
    if m:
        h=m.group("context").strip()
        if not re.search(r"(?i)\b(?:that|which|if)\b",mask_math(h)):
            return make(base,[h],[body],"source_intransitive_subject_assertion",
                "Unconditional source subject for retrieval; result verb retained")
    return None

def classify(base):
    body,_=source_body(base["statement"])
    if not body or EXTERNAL.search(body) or PLACEHOLDER.search(body):
        return None
    if IFF.search(mask_math(body)) or "\\begin" in body:
        return None
    for fn in (plain_setup,plain_subject):
        out=fn(base,body)
        if out:return out
    return None

def main():
    totals=Counter()
    summary=[]
    for b in BATCHES:
        w=Path("harvest/batches")/b
        d=p.load_rows(w/"pass2.jsonl","candidate_id")
        old=Counter(v["context_status"] for v in d.values())
        updated=[]
        for ident,v in sorted(d.items()):
            if v["context_status"]!="needs_structure":continue
            found=classify(v)
            if found:updated.append(found)
        if updated:
            target=w/"pass2_structural_plain_decisions.jsonl"
            p.atomic_text(target,"".join(json.dumps(v,ensure_ascii=False,sort_keys=True)+"\n" for v in updated))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(target),replace=True))
        final=p.load_rows(w/"pass2.jsonl","candidate_id")
        states=Counter(v["context_status"] for v in final.values())
        assert states["needs_context"]==old["needs_context"]
        assert states["needs_structure"]==old["needs_structure"]-len(updated)
        assert not p.load_rows(w/"pass3.jsonl","candidate_id")
        totals.update(states)
        summary.append({"batch":b,"structural_resolved":len(updated),
                        "structure_remaining":states["needs_structure"]})
    assert sum(totals.values())==10987
    result={"newly_structured":sum(x["structural_resolved"] for x in summary),
            "batches":summary,"statuses":dict(sorted(totals.items())),
            "proofs_read":False,"published_catalog_untouched":True}
    p.atomic_text(Path("harvest/PASS2_STRUCTURAL_PLAIN_FINAL_2026-10-28.json"),
                  json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()

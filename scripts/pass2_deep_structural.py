#!/usr/bin/env python3
"""Another conservative source-form Pass 2 review for ALL structural holdouts.

Does not inspect any proof, invent missing mathematical assumptions, promote
data, or touch published theorem records. All original LaTeX and provenance
stay intact; search interpretations are explicitly provisional.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from collections import Counter

try:
    from . import harvest_pipeline as p
    from .pass2_context_source_probe import BATCHES
    from .pass2_remaining_targeted import source_body
    from .pass2_hard_structures import mask_math, enum_blocks, list_items,logical_item,interpret as interpret_hard
    from .pass2_hard_followup import interpret_followup
    from .pass2_remaining_targeted import interpret_targeted
except ImportError:
    import harvest_pipeline as p
    from pass2_context_source_probe import BATCHES
    from pass2_remaining_targeted import source_body,interpret_targeted
    from pass2_hard_structures import mask_math,enum_blocks,list_items,logical_item,interpret as interpret_hard
    from pass2_hard_followup import interpret_followup

IFFF=re.compile(r"\bif\s+and\s+only\s+if\b",re.I)
TAIL_NOTE=re.compile(r"^(?:Moreover|In\s+particular|In\s+this\s+case|"
                      r"In\s+either\s+case|Further(?:more)?|Consequently|"
                      r"Thus|Therefore|Also)\b",re.I)
SETUP=re.compile(r"^(?:Let|Suppose|Assume|Fix|Consider|Given)\b",re.I)
CLAIM=re.compile(r"\b(?:there\s+(?:exists?|is|are)|"
                 r"the\s+following\s+(?:statements\s+)?hold|"
                 r"we\s+(?:have|obtain)|"
                 r"the\s+map\s+is|"
                 r"it\s+follows\s+that)\b",re.I)
CASE_HEAD=re.compile(
    r"^(?:(?:The|These)\s+following\s+(?:types\s+of|examples\s+of|"
    r"schemes|objects|categories|situations|cases)\b"
    r"|The\s+following\s+(?:categories|objects|types|cases)\b)",re.I)

def make(base,h,c,form,why,eq=None,cases=None):
    if not h or not c or any(not v.strip() for v in h+c):return None
    return {**base,"hypotheses":h,"conclusions":c,
            "context_status":"resolved","context_note":"",
            "review_method":"editorial",
            "split_confidence":"bounded_structural_editorial_unverified",
            "logical_form":form,
            "equivalence_sides":[[v] for v in eq] if eq else [],
            "structured_cases":cases or [],
            "statement_editorial_notes":"Additional Pass 2 source grammar: "+why+
              ". Unchanged original Stacks statement. No proof consulted or validity checked."}


def independent_list(base,body):
    blocks=enum_blocks(body)
    if not blocks or len(blocks)!=1:return None
    a,b=blocks[0]
    before=body[:a].strip()
    after=body[b:].strip()
    items=list_items(body,blocks[0])
    if not items or after or len(items)>14:return None
    if any(re.search(r"(?i)\b(?:and\s+so\s+on|etc\.?|add\s+more\s+here|to\s+do)\b",z) for z in items):return None
    if not CASE_HEAD.match(before):return None
    if IFFF.search(body) or re.search(r"\b(?:are|is)\s+equivalent\b",before,re.I):
        return None
    if not re.search(r"\b(?:are|is|have|has|define)\b",mask_math(before),re.I):
        return None
    if re.search(r"(?i)\b(?:assume|suppose|one\s+of\s+the\s+following\s+conditions)\b",before):
        return None
    # The heading is a source-authored predicate applying to each item;
    # do NOT turn it into a fabricated independent mathematical implication.
    if any(re.search(r"\b(?:and\s+only\s+if|if\s+and\s+only\s+if)\b",z,re.I) for z in items):
        return None
    cases=[{"hypotheses":[item],"conclusions":[before],
            "source_clause":item,"logical_form":"source_type_example"} for item in items]
    return make(base,items,[before],"source_classification_list",
                "Source says each listed type meets shared stated property; all source items retained",cases=cases)


def iff_plus_scoped_tail(base,body):
    blocks=enum_blocks(body)
    if not blocks or len(blocks)!=1:return None
    a,b=blocks[0]
    before=body[:a].strip()
    after=body[b:].strip()
    if not after or not TAIL_NOTE.match(after) or len(after)>1500:return None
    if not re.search(r"\b(?:are|is)\s+equivalent\b",before,re.I):return None
    items=list_items(body,blocks[0])
    if not items or len(items)<2 or len(items)>18:return None
    if re.search(r"(?i)\b(?:to\s+do|add\s+more\s+here|exercise\s+for\s+the\s+reader)\b",body):
        return None
    # Require direct source statements in header; conditions remain
    # bidirectional, not a one-way hypothesis to arbitrary tail.
    if not (SETUP.match(before) or re.match(r"^The\s+following\b",before,re.I)):
        return None
    h=[before]+items
    c=items+[after]
    cases=[{"logical_form":"equivalence","hypotheses":items,
            "conclusions":items,"source_clause":body[a:b],
            "equivalence_sides":items},
           {"logical_form":"scoped_consequence","hypotheses":[before],
            "conclusions":[after],"source_clause":after,
            "scope_note":"Extra source consequence is NOT an equivalent condition"}]
    return make(base,h,c,"equivalence_with_scoped_consequence",
                "Additional conclusion indexed separately from conditions; no new equivalence asserted",
                eq=items,cases=cases)


def explicit_result_after_source_setup(base,body):
    if not SETUP.match(body) or len(body)>2400:return None
    blocks=enum_blocks(body)
    if blocks is None:return None
    plain=mask_math(body)
    # Result words are meaningful after FULL setup sentence(s), and the
    # statement's source quantifiers remain with the entire asserted result.
    markers=[]
    for m in CLAIM.finditer(plain):
        if m.start()<20:continue
        if any(a<=m.start()<b for a,b in blocks):continue
        h,c=body[:m.start()].strip(),body[m.start():].strip()
        if not h or not c:continue
        if h.rstrip().endswith(("if","and","or","that","such that",":")):continue
        if not re.search(r"\.\s*$",h) and not re.search(r"\b(?:assume|let|suppose)\b",h,re.I):
            continue
        if re.search(r"\b(?:then|if\s+and\s+only\s+if)\b",mask_math(h),re.I):
            continue
        markers.append((h,c,m.group()))
    if not markers:return None
    h,c,word=markers[-1] if len(markers)==1 else markers[0]
    return make(base,[h],[c],"source_setup_then_statement",
                "Complete source setup before explicit assertion: "+word)


def reverse_if(base,body):
    if "\n\n" in body or len(body)>630 or "\\begin{" in body:return None
    if IFFF.search(body):return None
    plain=mask_math(body)
    hits=list(re.finditer(r"\bif\b",plain,re.I))
    if len(hits)!=1:return None
    m=hits[0]
    before,after=body[:m.start()].strip(),body[m.end():].strip()
    if not before or not after or re.search(r"\b(?:then|whenever|provided)\b",plain,re.I):
        return None
    if not re.search(r"\b(?:is|are|exists?|has|have|can|admits|defines)\b",plain[:m.start()],re.I):
        return None
    if re.search(r"\b(?:is|are|has|have|exists?)\b",plain[m.end():],re.I) is None:
        return None
    if before.endswith((":","such that","and","or")) or after.endswith((":","if")):
        return None
    return make(base,["If "+after],[before],
                "reverse_if_implication",
                "Mathematical source statement P if Q indexes Q as hypothesis and P as result")


def independent_short_claims(base,body):
    if len(body)>750 or "\\begin{" in body or IFFF.search(body):return None
    plain=mask_math(body)
    # Only 2 or 3 independent complete sentences, no implied
    # common conditions and no bibliographic display prose.
    cuts=list(re.finditer(r"\.\s+(?=[A-Z])",plain))
    if len(cuts) not in (1,2):return None
    pieces=[];st=0
    for m in cuts:
        pieces.append(body[st:m.start()+1].strip());st=m.end()
    pieces.append(body[st:].strip())
    if not all(re.match(r"^(?:Any|Every|Each|A|An|The)\s+",s,re.I) for s in pieces):
        return None
    if any(re.search(r"\b(?:if|given|assume|suppose|provided|there\s+exists)\b",mask_math(s),re.I) for s in pieces):
        return None
    cases=[]
    for s in pieces:
        match=re.match(r"^(?P<subject>(?:Any|Every|Each|A|An|The)\s+.{4,130}?)\s+"
                       r"(?:is|are|has|have|satisfies|defines)\s+\S+",s,re.S|re.I)
        if not match:return None
        subject=match.group("subject").strip()
        cases.append({"hypotheses":[subject],"conclusions":[s],
                      "source_clause":s,"logical_form":"source_unconditional_claim"})
    return make(base,[v["hypotheses"][0] for v in cases],
                [v["conclusions"][0] for v in cases],
                "collection_of_source_assertions",
                "Distinct unconditional source claims indexed by their explicit subjects",cases=cases)


def try_hard(base):
    source=base["statement"].strip()
    body,removed=source_body(source)
    if not body:return None,"empty statement"
    if len(body)>6500:return None,"too_long_for_bounded_pass"
    if re.search(r"(?i)\b(?:add\s+more\s+here|to\s+do|we\s+should\s+prove)\b",body):
        return None,"source_editorial_placeholder"
    if removed:
        for fn in (interpret_targeted,interpret_followup,interpret_hard):
            try:
                out,_=fn({"statement":body})
                if out and out.get("hypotheses") and out.get("conclusions"):
                    return make(base,out["hypotheses"],out["conclusions"],
                         out.get("logical_form","source_assertion"),
                         "Source citation preface removed from grammatical interpretation",
                         eq=[x[0] for x in out.get("equivalence_sides",[]) if len(x)==1],
                         cases=out.get("structured_cases",[])),"metadata_normalized"
            except (KeyError,ValueError,TypeError,IndexError):
                pass
    for fn in (iff_plus_scoped_tail,independent_list,explicit_result_after_source_setup,
               reverse_if,independent_short_claims):
        out=fn(base,body)
        if out:return out,fn.__name__
    return None,"needs_mathematical_editorial_interpretation"


def run(args):
    overall=Counter()
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        existing=p.load_rows(w/"pass2.jsonl","candidate_id")
        edits=[];still=[];forms=Counter();reason=Counter()
        for ident,v in sorted(existing.items()):
            if v["context_status"]!="needs_structure":continue
            out,why=try_hard(v)
            if out:
                edits.append(out);forms[why]+=1
            else:
                still.append({"candidate_id":ident,"source_statement":v["statement"],
                              "reason":why,"queue":"pass2_higher_thinking_after_additional_review"})
                reason[why]+=1
        if edits:
            d=w/"pass2_deep_structural_decisions.jsonl"
            p.atomic_text(d,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in edits))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(d),replace=True))
        p.atomic_text(w/"pass2_structural_remaining_latest.jsonl",
            "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in still))
        final=p.load_rows(w/"pass2.jsonl","candidate_id")
        stats=Counter(x["context_status"] for x in final.values())
        out={"initial_structural_candidates":len(still)+len(edits),
             "newly_resolved":len(edits),"structural_still_open":len(still),
             "forms":dict(sorted(forms.items())),"unresolved_reasons":dict(sorted(reason.items())),
             "status_after":dict(sorted(stats.items())),
             "statement_only":True,"proofs_read":False}
        p.atomic_text(w/"pass2_deep_structural_summary.json",
                      json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps({"batch":batch,**out},sort_keys=True))
        overall.update({"new_resolved":len(edits),"remain_structural":len(still)})
    print(json.dumps({"aggregate":dict(overall)}))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--noop",action="store_true")
    run(parser.parse_args())

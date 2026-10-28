#!/usr/bin/env python3
"""Bounded Pass 2 named Situation context extraction, all three Stacks batches.

Source version is checked before use by the calling workflow. Read labeled
non-proof Situation/notation/setup environments in the original source;
nothing is semantically researched or proof-checked. Do not accept ambiguous
structures. Retain full original statement and source excerpts for audit.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from collections import Counter
try:
    from . import harvest_pipeline as p
    from .pass2_context_source_probe import get_index, BATCHES
    from .pass2_hard_followup import interpret_followup
    from .pass2_hard_structures import interpret as interpret_hard, mask_math
    from .pass2_remaining_targeted import interpret_targeted, source_body
    from .pass2_structural_light import split as structural_split
except ImportError:
    import harvest_pipeline as p
    from pass2_context_source_probe import get_index, BATCHES
    from pass2_hard_followup import interpret_followup
    from pass2_hard_structures import interpret as interpret_hard,mask_math
    from pass2_remaining_targeted import interpret_targeted,source_body
    from pass2_structural_light import split as structural_split

REF = re.compile(
    r"^(?:(?:In|Under|With)\s+(?:the\s+)?(?:Situation|situation)\s*"
    r"|(?:With\s+)?(?:the\s+)?notation\s+(?:from|of)\s+(?:Situation|situation)\s*)"
    r"\\ref\{(?P<label>[^{}]+)\}\s*[.,;:]?\s*",
    re.I)
SIMPLE_THEN=re.compile(r"^\s*(?:Then|Hence|Therefore)\b\s*[,:]?\s*",re.I)
START_CLAIM=re.compile(
    r"^(?:There|The|This|These|It|We|For|Any|Every|Each|An|A |"
    r"In\s+(?:this|the|that)|Under|One|Moreover)\b",re.I)
UNSAFE=re.compile(
    r"(?i)\b(?:assumptions\s+and\s+notation\s+as\s+in|"
    r"in\s+(?:the\s+)?(?:situation|setup)\s+(?:above|below)|"
    r"with\s+notation\s+as\s+(?:in|above)|"
    r"as\s+(?:defined|described)\s+above)\b")
OPEN_PREMISE=re.compile(r"(?i)\b(?:Assume|Suppose|Given|Provided|If|Whenever)\s*:?\s*$")

def decode(source):
    body,removed=source_body(source)
    return body

def split_source(body):
    """Only source evidence, including source-native biconditional indexing."""
    for fn in (interpret_followup,interpret_targeted,interpret_hard):
        try:
            if fn is interpret_followup:
                v,_=fn({"statement":body})
            elif fn is interpret_targeted:
                v,_=fn({"statement":body})
            else:
                v,_=fn({"statement":body})
            if v and v.get("hypotheses") and v.get("conclusions"):
                return v,"explicit source grammar"
        except (KeyError,ValueError,IndexError):
            # Some callers accept a full Pass 2 record; fail closed.
            pass
    h,c,reason=structural_split(body)
    if h and c:
        return {"hypotheses":[h],"conclusions":[c],
                "logical_form":"source_setup_assertion",
                "equivalence_sides":[],"structured_cases":[]},reason
    # Then P: an initial 'Then' asserts the next clause under the
    # externally recovered Situation. It is NOT treated as an orphan antecedent.
    m=SIMPLE_THEN.match(body)
    if m and body[m.end():].strip():
        return {"hypotheses":[],"conclusions":[body[m.end():].strip()],
                "logical_form":"assertion_under_named_situation",
                "equivalence_sides":[],"structured_cases":[]}, "explicit Then after recovered Situation"
    if re.match(r"^If\b",body,re.I):
        masked=mask_math(body)
        m=re.search(r"\bthen\b",masked,re.I)
        if m and body[:m.start()].strip() and body[m.end():].strip():
            return {"hypotheses":[body[:m.start()].strip()],
                    "conclusions":[body[m.end():].strip()],
                    "logical_form":"implication_under_named_situation",
                    "equivalence_sides":[],"structured_cases":[]}, "source-native If/then under named Situation"
    # A clearly asserted unconditional claim under a named Situation is
    # structurally complete even when there is no separate local 'if'.
    # The entire claim remains the conclusion, not a fabricated paraphrase.
    if len(body)<=1550 and START_CLAIM.match(body) and not OPEN_PREMISE.search(body):
        if not re.search(r"(?i)\b(?:the\s+following\s+assumptions|assume\s+the\s+following|"
                         r"the\s+following\s+conditions\s+hold)\b",body):
            if "\\begin{enumerate}" not in body and "\\begin{itemize}" not in body:
                return {"hypotheses":[],
                        "conclusions":[body],
                        "logical_form":"source_assertion_under_named_situation",
                        "equivalence_sides":[],"structured_cases":[]}, "full source assertion under named situation; not a directional inference"
    return None,"named context recovered; theorem-level hypothesis/result boundary still ambiguous"

def prepare(record,sourceinfo,ref_label,sourcefile,revision,body,recovered,reason):
    # Never overwrite raw source or mark proof-scanned. Preserve all
    # condition lists and bidirectional equivalence metadata.
    hypotheses=[f"Standing assumptions and notation from Stacks Situation \\ref{{{ref_label}}}:\n{sourceinfo['text']}"]
    hypotheses.extend(recovered.get("hypotheses",[]))
    conclusions=recovered["conclusions"]
    contexts=[{"label":ref_label,"kind":sourceinfo["kind"],"filename":sourcefile,
               "statement_line":sourceinfo["line"],"source_revision":revision,
               "source_statement":sourceinfo["text"]}]
    return {
        **record,
        "hypotheses":hypotheses,"conclusions":conclusions,
        "context_status":"resolved","context_note":"",
        "review_method":"editorial",
        "split_confidence":"pinned_situation_statement_expansion_unverified",
        "logical_form":recovered.get("logical_form","assertion_under_named_situation"),
        "equivalence_sides":recovered.get("equivalence_sides",[]),
        "structured_cases":recovered.get("structured_cases",[]),
        "local_context_used":contexts,
        "statement_editorial_notes":"Pass 2 same-file named Situation context explicitly recovered at pinned source; "
            +reason+". Full source theorem statement retained; no proof analysis or mathematical validation.",
    }

def run(args):
    root=Path(args.source_root)
    summary={}
    combined=Counter()
    wdirs=[Path("harvest/batches")/v for v in BATCHES]
    source_by_batch={str(w):p.load_rows(w/"pass1.jsonl","candidate_id") for w in wdirs}
    files=set()
    for w in wdirs:
        raw=source_by_batch[str(w)]
        files.update(v["source"]["filename"] for v in raw.values())
    idx=get_index(root,files)
    for w in wdirs:
        raw=source_by_batch[str(w)]
        current=p.load_rows(w/"pass2.jsonl","candidate_id")
        resolved=[]
        recovered_pending=[]
        unresolved=[]
        reasons=Counter()
        for ident,p2 in sorted(current.items()):
            if p2["context_status"]!="needs_context":
                continue
            original=p2["statement"]
            body=decode(original)
            m=REF.match(body)
            if not m:
                reasons["no_direct_named_situation_header"]+=1
                continue
            label=m.group("label")
            filename=raw[ident]["source"]["filename"]
            revision=raw[ident]["source"]["revision"]
            context=idx.get((filename,label))
            if not context or context["kind"] not in ("situation","setup","notation"):
                reasons["situation_not_available_same_source"]+=1
                continue
            ctxt=context["text"]
            if len(ctxt)<25 or len(ctxt)>2500:
                reasons["context_too_long_or_short"]+=1
                continue
            if not re.match(r"^(?:situation|setup|notation)-",label):
                reasons["label_not_a_situation"]+=1
                continue
            remainder=body[m.end():].strip()
            if not remainder:
                reasons["empty_result_after_context_header"]+=1
                continue
            if UNSAFE.search(remainder):
                reasons["secondary_external_context_dependency"]+=1
                continue
            if re.search(r"\\ref\{(?:situation|setup)-[^{}]+\}",ctxt):
                reasons["context_itself_inherits_another_situation"]+=1
                continue
            got,why=split_source(remainder)
            if not got:
                recovered_pending.append({"candidate_id":ident,"source_file":filename,
                    "source_revision":revision,"context_label":label,
                    "context_statement":ctxt,"remaining_statement":remainder,
                    "reason":why,
                    "queue":"pass2_context_recovered_structure_pending"})
                reasons["context_recovered_but_structure_complex"]+=1
                continue
            updated=prepare(p2,context,label,filename,revision,body,got,why)
            resolved.append(updated)
            reasons["context_and_structure_resolved"]+=1
        if resolved:
            decision_file=w/"pass2_context_expanded_decisions.jsonl"
            p.atomic_text(decision_file,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in resolved))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(decision_file),replace=True))
        p.atomic_text(w/"pass2_context_recovered_structure_pending.jsonl",
            "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in recovered_pending))
        final=p.load_rows(w/"pass2.jsonl","candidate_id")
        statuses=Counter(v["context_status"] for v in final.values())
        stat={"initial_context_candidates":sum(v["context_status"]=="needs_context" for v in current.values()),
              "resolved_via_pinned_situation":len(resolved),
              "context_found_but_structure_pending":len(recovered_pending),
              "reason_counts":dict(sorted(reasons.items())),
              "statuses_after":dict(sorted(statuses.items())),
              "source_revision":args.revision,
              "statement_source_only":True,"proofs_read":False}
        p.atomic_text(w/"pass2_context_expansion_summary.json",json.dumps(stat,indent=2,sort_keys=True)+"\n")
        summary[w.name]=stat
        combined.update({"new_resolved":len(resolved),"recovered_pending":len(recovered_pending)})
    print(json.dumps({"combined":dict(combined),
        "by_batch":summary},indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",default="upstream/stacks")
    ap.add_argument("--revision",default="a04446e57ec1fbc252a871afcec7752fb2807b14")
    run(ap.parse_args())

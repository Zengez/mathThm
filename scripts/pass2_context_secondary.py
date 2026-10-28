#!/usr/bin/env python3
"""Recover further source-label context / mistaken context triggers for Stacks Pass 2.

Unlike a purely mechanical regex unflagging, this only resolves:
 (A) references confined to bibliographical metadata before the theorem;
 (B) locally displayed diagrams mistakenly read as 'following diagram';
 (C) a direct named lemma's inherited source assumptions/notation, recovered
     from the pinned same-file original lemma statement;
 (D) a definitional citation alongside otherwise self-contained grammar.

A declaration like 'as in Section' remains unresolved unless its precise
standing context can be established by an editorial review. Never read proofs.
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
    from .pass2_fast_stacks import CONTEXT_DEPENDENCY
    from .pass2_hard_structures import interpret as interpret_hard,mask_math
    from .pass2_hard_followup import interpret_followup
    from .pass2_remaining_targeted import interpret_targeted,source_body
    from .pass2_structural_light import split as source_split
except ImportError:
    import harvest_pipeline as p
    from pass2_context_source_probe import get_index,BATCHES
    from pass2_fast_stacks import CONTEXT_DEPENDENCY
    from pass2_hard_structures import interpret as interpret_hard,mask_math
    from pass2_hard_followup import interpret_followup
    from pass2_remaining_targeted import interpret_targeted,source_body
    from pass2_structural_light import split as source_split

LEMMA_HEAD=re.compile(
    r"^(?:Assumptions\s+and\s+notation|"
    r"(?:With|Using)\s+(?:the\s+)?(?:same\s+)?notation|"
    r"(?:As|In)\s+(?:the\s+)?(?:setting|situation))"
    r"\s+(?:as|from|of)\s+in\s+(?:(?:\w+\s+){0,4}?,?\s*)?"
    r"(?:Lemma|Proposition|Theorem)\s*\\ref\{(?P<label>[^{}]+)\}\s*"
    r"[.,;:]?\s*",re.I)

# Common exact header not covered above: 'With notation as in Lemma REF'.
LEMMA_HEAD2=re.compile(
    r"^(?:(?:Assumptions\s+and\s+notation|With\s+notation)\s+as\s+in\s+"
    r"|(?:In\s+the\s+setting\s+of)\s+)"
    r"(?:[A-Za-z ]+,\s*)?(?:Lemma|Proposition|Theorem)\s*"
    r"\\ref\{(?P<label>[^{}]+)\}\s*[.,;:]?\s*",re.I)

DEFINITION_CITE=re.compile(
    r"(?i)\bas\s+in\s+(?:[A-Z][A-Za-z\s]+,\s*)?(?:Definition|Remark)\s+\\ref\{[^{}]+\}")
REF_ANY=re.compile(r"\\ref\{([^{}]+)\}")
NO_STANDING=re.compile(
    r"(?i)\b(?:with\s+notation\s+as\s+above|"
    r"assumptions\s+and\s+notation\s+as\s+in|"
    r"in\s+the\s+situation\s+(?:above|below)|"
    r"in\s+situation\s+\\ref|"
    r"as\s+(?:defined|constructed)\s+(?:above|previously))\b")
CLAIM_START=re.compile(
    r"^(?:Then|There|The|This|These|It|We|For|Any|Every|Each|An|A|"
    r"In\s+(?:this|the)|One|Moreover)\b",re.I)
INTERNAL_DIAGRAM=re.compile(r"(?i)\bthe\s+following\s+diagram\b")
SOURCE_REF_PREFIX=re.compile(r"^\s*\\begin\{(?:reference|history)\}",re.I)


def parse_statement(body):
    """Return (structured, reason) or (None, reason)."""
    for fn in (interpret_followup,interpret_targeted,interpret_hard):
        try:
            out,_=fn({"statement":body})
            if out and out.get("hypotheses") and out.get("conclusions"):
                return out,"source grammar / equivalence"
        except (KeyError,ValueError,TypeError,IndexError):
            pass
    h,c,reason=source_split(body)
    if h and c:
        return {"hypotheses":[h],"conclusions":[c],
                "logical_form":"explicit_source_grammar",
                "equivalence_sides":[],"structured_cases":[]},reason
    return None,reason


def finished(base,out,method,reason,context=None):
    if not out or not out.get("hypotheses") or not out.get("conclusions"):
        return None
    return {**base,"hypotheses":out["hypotheses"],
        "conclusions":out["conclusions"],
        "context_status":"resolved","context_note":"",
        "review_method":"editorial",
        "split_confidence":method,
        "logical_form":out.get("logical_form","source_statement"),
        "equivalence_sides":out.get("equivalence_sides",[]),
        "structured_cases":out.get("structured_cases",[]),
        "local_context_used":context or base.get("local_context_used",[]),
        "statement_editorial_notes":"Pass 2 source-only: "+reason+
           ". Exact original source retained; no mathematical validation or proof review.",
    }


def lemma_context(ref,statement):
    """Lexically recover only a lemma's own source setup, not its proof."""
    source=statement["text"]
    # A source lemma's result is not automatically a new hypothesis.
    out,_=parse_statement(source)
    if out and out.get("hypotheses"):
        setup=out["hypotheses"]
        if source.strip().startswith("Let") and any(x.startswith("Let") for x in setup):
            return [x for x in setup if not x.strip().lower().startswith("the following")]
    # No safe identification; caller may keep source text as contextual metadata
    # but MUST NOT mark the theorem resolved through invented premises.
    return []


def try_secondary(base,raw,index):
    original=base["statement"]
    body,had_metadata=source_body(original)
    if not body:return None,"empty body after source metadata"
    if SOURCE_REF_PREFIX.match(body):
        return None,"unparsed source preface"
    file=raw["source"]["filename"]
    revision=raw["source"]["revision"]

    # Case A: the only trigger was prose in a bibliography/reference env.
    if had_metadata and not CONTEXT_DEPENDENCY.search(body):
        out,reason=parse_statement(body)
        if out:
            return finished(base,out,"metadata_only_context_false_positive",
                            "Dependency trigger was bibliographic, not a missing theorem assumption"),"metadata_only"

    # Case B: no external context: 'the following diagram' literally refers to
    # diagram *inside* this same theorem statement. Do not strip diagram.
    triggers=list(CONTEXT_DEPENDENCY.finditer(body))
    if triggers and all(INTERNAL_DIAGRAM.fullmatch(m.group().strip()) for m in triggers):
        if ("\\xymatrix" in body or "\\begin{diagram}" in body):
            out,reason=parse_statement(body)
            if out:
                return finished(base,out,"internal_diagram_source_grammar",
                    "All context-trigger phrases refer to a diagram within this same statement"),"internal_diagram"
            return None,"internal diagram detected; logical clause boundary remains open"

    # Case C: context inherited from exact earlier lemma, with source setup.
    m=LEMMA_HEAD2.match(body) or LEMMA_HEAD.match(body)
    if m:
        label=m.group("label")
        source=index.get((file,label))
        if not source or source["kind"] not in ("lemma","proposition","theorem"):
            return None,"named theorem context not available in same source"
        if len(source["text"])>2500:
            return None,"named theorem context unusually large"
        setup=lemma_context(label,source)
        if not setup:
            return None,"referenced theorem does not expose a safe standing setup"
        rest=body[m.end():].strip()
        if not rest or NO_STANDING.search(rest):
            return None,"additional unstated assumptions after named lemma"
        out,why=parse_statement(rest)
        if not out:
            return None,"named lemma available, but current statement's structure ambiguous"
        local={
            "label":label,"kind":source["kind"],
            "filename":file,"statement_line":source["line"],
            "source_revision":revision,
            "context_source_statement":source["text"],
            "context_source_hypotheses":setup,
        }
        data=dict(out)
        data["hypotheses"]=[f"Standing assumptions of Stacks {source['kind']} \\ref{{{label}}}: "+s
                            for s in setup]+out["hypotheses"]
        # The source lemma's theorem conclusion is NOT copied as an assumption.
        return finished(base,data,"pinned_lemma_setup_expansion_unverified",
           "Standing source-lemma setup recovered, without treating that lemma's result as another premise",
           [local]),"named_lemma"

    # Case D: if every 'as in' style trigger names only a specific Definition
    # or Remark and is in *statement provenance* (not missing Situation
    # hypotheses), a direct source grammatical split may be safely indexed.
    if not NO_STANDING.search(body):
        if triggers and all(("as in" in m.group().lower()
                             or "in the setting of" in m.group().lower()) for m in triggers):
            refs=DEFINITION_CITE.findall(body)
            if refs and len(refs)==len(triggers):
                out,why=parse_statement(body)
                if out:
                    return finished(base,out,"definition_citation_source_grammar_unverified",
                                    "Explicit definitional reference is not a missing premise"),"definition_citation"
    return None,"external context or structure still needs editorial work"


def run(args):
    root=Path(args.source_root)
    files=set()
    rows_by_batch={}
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        raw=p.load_rows(w/"pass1.jsonl","candidate_id")
        current=p.load_rows(w/"pass2.jsonl","candidate_id")
        rows_by_batch[batch]=(w,raw,current)
        files.update(v["source"]["filename"] for v in raw.values())
    index=get_index(root,files)
    for batch,(w,raw,current) in rows_by_batch.items():
        updated=[];reasons=Counter();classes=Counter()
        for ident,v in sorted(current.items()):
            if v["context_status"]!="needs_context":continue
            out,reason=try_secondary(v,raw[ident],index)
            if out:
                updated.append(out);classes[reason]+=1
            else:reasons[reason]+=1
        if updated:
            decisions=w/"pass2_context_secondary_decisions.jsonl"
            p.atomic_text(decisions,"".join(json.dumps(v,ensure_ascii=False,sort_keys=True)+"\n" for v in updated))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(decisions),replace=True))
        after=p.load_rows(w/"pass2.jsonl","candidate_id")
        counts=Counter(x["context_status"] for x in after.values())
        summary={"batch":batch,"initial_context_pending":sum(v["context_status"]=="needs_context" for v in current.values()),
                 "new_resolved":len(updated),
                 "resolution_types":dict(sorted(classes.items())),
                 "deferred_reasons":dict(sorted(reasons.items())),
                 "status_after":dict(sorted(counts.items())),
                 "proofs_read":False,
                 "math_validity_assessed":False}
        p.atomic_text(w/"pass2_context_secondary_summary.json",json.dumps(summary,indent=2,sort_keys=True)+"\n")
        print(json.dumps(summary,sort_keys=True))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",default="upstream/stacks")
    run(ap.parse_args())

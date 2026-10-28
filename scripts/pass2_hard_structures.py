#!/usr/bin/env python3
"""Interpret explicit logical forms in the original 827 Pass 2 hard cases.

THIS IS STATEMENT ANALYSIS ONLY. No proofs, mathematical research, truth
assessment, or site publication. Never turn an equivalence into a one-way
implication. Keep compound conditional clauses as compound clauses.
Use mechanical/source-syntax confidence flags, not "verified" terminology.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

try:
    from . import harvest_pipeline as pipe
except ImportError:
    import harvest_pipeline as pipe

OPEN = r"\begin{enumerate}"
CLOSE = r"\end{enumerate}"
ITEM = re.compile(r"\\item(?:\s*\[[^\]]{0,30}\])?\s*")
INTRO = re.compile(r"^(?:Let|Suppose|Assume|Fix|Take|Consider|Write|Set)\b", re.I)
EQUIV = re.compile(
    r"\b(?:the\s+following|following\s+(?:conditions|properties|assertions|statements)|"
    r"these\s+(?:conditions|statements|assertions|properties))\s+"
    r"(?:are|is)\s+equivalent\b", re.I)
AMBIGUOUS = re.compile(
    r"\b(?:add more here|to do|we should prove|exercise for the reader|"
    r"we leave it to the reader)\b", re.I)
CROSS_CONTEXT = re.compile(
    r"\b(?:as\s+above|as\s+in\s+the\s+previous|in\s+situation|"
    r"under\s+the\s+assumptions\s+(?:of|above)|"
    r"with\s+(?:the\s+)?(?:notation|assumptions|conventions)\s+(?:of|as\s+in))\b",
    re.I)
SENTENCE_HEAD = re.compile(
    r"^(?:There|The|This|These|It|We|For|Given|Any|Every|Each|An|A|"
    r"In\s+(?:this|that|the)|Under|If|As|One|Moreover|Also|Hence|"
    r"Consequently|To\s+give|Being|From)\b", re.I)


def mask_math(text: str) -> str:
    """Replace math spans, retaining length and newlines for safe punctuation search."""
    chars = list(text)
    patterns = (
        r"(?<!\\)\$\$[\s\S]*?(?<!\\)\$\$",
        r"(?<!\\)\$[^\$]*?(?<!\\)\$",
        r"\\\[[\s\S]*?\\\]",
        r"\\\([\s\S]*?\\\)",
    )
    for p in patterns:
        for m in re.finditer(p, text):
            for i in range(m.start(), m.end()):
                if chars[i] != "\n":
                    chars[i] = "~"
    return "".join(chars)


def enum_blocks(text):
    """Return outermost top-level enumerate blocks, including their interiors.

    Reject malformed environments, retain exact original indices/TeX.
    """
    tokens = re.finditer(r"\\(?:begin|end)\{enumerate\}", text)
    depth = 0
    start = None
    blocks = []
    for m in tokens:
        if m.group().startswith("\\begin"):
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth < 0:
                return None
            if depth == 0:
                blocks.append((start, m.end()))
    return blocks if depth == 0 else None


def list_items(text: str, outer):
    """Split only top-level items, never flatten nested conditions into claims."""
    a,b=outer
    begin = a+len(OPEN)
    end = b-len(CLOSE)
    inner = text[begin:end]
    # Mask nested enumerate environments so \item within them isn't top-level.
    mask = list(inner)
    nesting=0
    pos=0
    for m in re.finditer(r"\\(?:begin|end)\{enumerate\}", inner):
        if nesting:
            for i in range(pos, m.start()):
                mask[i]=" "
        if m.group().startswith("\\begin"):
            if nesting==0:
                start=m.start()
            nesting+=1
        else:
            nesting-=1
            if nesting==0:
                for i in range(start, m.end()):
                    mask[i]=" "
        pos=m.end()
    if nesting:
        return None
    # Mask all characters from each nested block through its closing marker;
    # the enclosing source item retains the original nested text.
    flat="".join(mask)
    markers=list(ITEM.finditer(flat))
    if not markers or flat[:markers[0].start()].strip():
        return None
    items=[inner[m.end():markers[i+1].start() if i+1<len(markers) else len(inner)].strip()
           for i,m in enumerate(markers)]
    if not all(items):
        return None
    return items


def safe_setup(text):
    """Split initial complete Let/Assume/Consider sentences without changing scope."""
    masked=mask_math(text)
    ends=[m for m in re.finditer(r"\.\s+(?=[A-Z\\$\\])",masked)]
    if not INTRO.match(text):
        return None
    last=0
    for m in ends:
        # Keep successive source setup sentences together. A quantified claim
        # beginning "Given ..." is not automatically a setup.
        piece=text[last:m.start()+1].strip()
        if not piece or not INTRO.match(piece):
            break
        last=m.end()
        rest=text[last:].lstrip()
        if not rest:
            break
        if SENTENCE_HEAD.match(rest) and not INTRO.match(rest):
            return text[:last].strip(), rest
    return None


def context_claim(text):
    """Explicit initial hypotheses followed by an asserted result."""
    split=safe_setup(text)
    if not split:
        return None
    h,c=split
    if not c:
        return None
    return h,c


def predicate_assertion(text):
    """Conservative simple universal property. Preserve the entire source claim.

    The hypothesis side is a source subject phrase, the result is the full
    original assertion. This is intentional rather than fabricating a new
    conditional statement. UI must eventually improve display tags.
    """
    s=text.strip()
    if len(s)>270 or "\n\n" in s:
        return None
    if re.search(r"\\(?:begin|end)\{|\\ref\{|\\cite",s) or EQUIV.search(s):
        return None
    if re.search(r"\bif\s+and\s+only\s+if\b|\bif\b.+\bthen\b",s,re.I):
        return None
    m=re.match(r"^(?P<subject>(?:Any|Every|Each|A|An|The)\s+"
       r".{5,180}?)\s+(?P<verb>is|are|has|have|admits|defines|exists|"
       r"can\s+be|can\s+have)\s+(?P<pred>[^.]+)\.?$",s,re.S|re.I)
    if not m:
        return None
    subject=m.group("subject").strip()
    pred=m.group("pred").strip()
    # If a modifier contains a verb, this source-based split can go wrong.
    if re.search(r"\b(?:is|are|has|have|exists)\b",subject,re.I):
        return None
    if not subject or not pred or re.search(r"\b(?:which|that|such\s+that)\b",subject,re.I):
        return None
    return subject,s


def split_equivalence(text, block, items):
    a,b=block
    before=text[:a].strip()
    after=text[b:].strip().strip(".")
    m=list(EQUIV.finditer(before))
    if not m or len(items)<2:
        return None,"not an explicit equivalence"
    if after:
        return None,"equivalence has additional asserted clauses requiring interpretation"
    if any(AMBIGUOUS.search(x) for x in items):
        return None,"equivalence contains a source editorial placeholder"
    head=before[:m[-1].start()].strip()
    tail=before[m[-1].end():].strip()
    if tail.strip(" :.\n\t"):
        return None,"text between equivalence header and conditions"
    # Context can be the direct Let setup, but never silently invent it.
    if not head or not INTRO.match(head):
        return None,"equivalence with implicit/unintroduced standing assumptions"
    if head.endswith("if") or head.endswith("such that"):
        return None,"equivalence context has open condition"
    return {
        # MathThm decision (2026-10-23): for an equivalence each condition
        # belongs to BOTH searchable sides. Do not create duplicate entries.
        "hypotheses":[head]+items,
        "conclusions":list(items),
        "logical_form":"equivalence",
        "equivalence_sides":[[item] for item in items],
        "structured_cases":[],
        "reason":"Bidirectional equivalence: every equivalent condition appears on both search sides, one canonical theorem",
    },None


def split_enumeration(text, block, items):
    a,b=block
    before=text[:a].strip()
    after=text[b:].strip()
    if not before or not items:
        return None,"enumerated result lacks setup/context"
    if re.search(r"\b(?:suppose|assume|given)\s*:?\s*$",before,re.I):
        return None,"list may contain assumptions, not conclusions"
    if re.search(r"\b(?:one\s+of\s+the\s+following|in\s+each\s+of\s+the\s+following|"
                 r"the\s+following\s+are\s+conditions|following\s+conditions\s+hold)\b",before,re.I):
        return None,"cases may be alternative hypotheses rather than results"
    # Explicit THEN before list or complete setup sentences preceding it.
    marker=re.search(r"\b(?:then|the\s+following\s+(?:statements\s+)?hold|we\s+have)\s*:?\s*$",before,re.I)
    if marker:
        h=before[:marker.start()].strip()
    else:
        h=before.strip()
    if not h or not INTRO.match(h):
        return None,"no explicit theorem-level hypothesis/setup"
    if len(items)>16:
        return None,"large list: too many independent clauses for light interpretation"
    if any(AMBIGUOUS.search(x) for x in items):
        return None,"editorial placeholder inside result list"
    # A tail can be a further assertion. If it depends on a case or gives
    # scope-sensitive extra conditions, don't rewrite it into an unconditional
    # claim. Keep cases together for higher review.
    if after:
        if re.match(r"^(?:Moreover|In particular|Also|Consequently|Furthermore)\b",after,re.I) and \
           len(after)<600 and "if and only if" not in after.lower():
            clauses=items+[after]
        else:
            return None,"additional clauses following list require scope interpretation"
    else:
        clauses=items
    cases=[]
    for item in clauses:
        cases.append({"hypotheses":[h],
                      "conclusions":[item],
                      "clause_is_conditional":bool(re.search(r"\b(?:if|whenever|provided)\b",item,re.I))})
    return {
        "hypotheses":[h],
        "conclusions":clauses,
        "logical_form":"conjunction_of_source_clauses",
        "equivalence_sides":[],
        "structured_cases":cases,
        "reason":"Source enumerates asserted clauses under common setup; conditional clauses retained verbatim",
    },None


def interpret(p2):
    text=p2["statement"].strip()
    if AMBIGUOUS.search(text):
        return None,"source appears to include unfinished editorial text"
    if CROSS_CONTEXT.search(text):
        return None,"statement appears dependent on another source setup or definition"
    if len(text)>5000:
        return None,"very long statement: reserved for higher effort"
    blocks=enum_blocks(text)
    if blocks is None:
        return None,"malformed or unbalanced enumerate structure"
    if blocks:
        if len(blocks)!=1:
            # Some have setup and results lists separately, with clear
            # 'Then'; split at that explicit boundary outside lists.
            candidates=[]
            for m in re.finditer(r"\bthen\b",mask_math(text),re.I):
                if not any(a <= m.start() < b for a,b in blocks):
                    candidates.append(m)
            if len(candidates)==1:
                m=candidates[0]
                h,c=text[:m.start()].strip(),text[m.end():].strip()
                if h and c and INTRO.match(h):
                    return {
                        "hypotheses":[h],"conclusions":[c],
                        "logical_form":"implication_with_structured_clauses",
                        "equivalence_sides":[],
                        "structured_cases":[],
                        "reason":"Explicit top-level THEN separates nested premise and result lists",
                    },None
            return None,"multiple enumerations or nested premises require contextual reasoning"
        block=blocks[0]
        items=list_items(text,block)
        if not items:
            return None,"could not safely identify top-level list items"
        m=EQUIV.search(text[:block[0]])
        if m:
            return split_equivalence(text,block,items)
        return split_enumeration(text,block,items)
    # No source enumerations: handle explicit source-native contexts.
    candidate=context_claim(text)
    if candidate:
        h,c=candidate
        if re.search(r"(?<![A-Za-z])(?:then|if\s+and\s+only\s+if)\b",h,re.I):
            return None,"possible nested conditional boundary"
        return {
            "hypotheses":[h],"conclusions":[c],
            "logical_form":"source_setup_then_assertion",
            "equivalence_sides":[],"structured_cases":[],
            "reason":"Complete initial setup sentences followed by asserted source text",
        },None
    candidate=predicate_assertion(text)
    if candidate:
        h,c=candidate
        return {
            "hypotheses":[h],"conclusions":[c],
            "logical_form":"source_universal_predicate",
            "equivalence_sides":[],"structured_cases":[],
            "reason":"Source subject recognized; full assertion preserved as result to avoid speculative rewording",
        },None
    return None,"requires higher-thinking semantic boundary interpretation"


def run(args):
    w=Path(args.workdir)
    initial=pipe.load_rows(w/"pass2_higher_thinking.jsonl","candidate_id")
    existing=pipe.load_rows(w/"pass2.jsonl","candidate_id")
    raw=pipe.load_rows(w/"pass1.jsonl","candidate_id")
    remaining=[]
    changes=[]
    patterns=Counter()
    for ident,oldq in sorted(initial.items()):
        current=existing.get(ident)
        if not current:
            raise ValueError(f"{ident}: missing baseline Pass 2 record")
        if current["context_status"]=="resolved":
            continue
        if current["context_status"]!="needs_structure":
            # Another concurrent review might have reclassified it.
            remaining.append({**oldq,"latest_context_status":current["context_status"],
                             "higher_thinking_reason":"Previously reclassified; no overwrite"})
            continue
        out,reason=interpret(current)
        if out:
            updated={
                **current,**out,
                "candidate_id":ident,
                "context_status":"resolved",
                "context_note":"",
                "review_method":"mechanical_syntax",
                "split_confidence":"source_structure_interpretation_unverified",
                "statement_editorial_notes":out["reason"]+
                    ". Statement interpretation, no proof analysis or mathematical validation.",
            }
            changes.append(updated)
            patterns[updated["logical_form"]]+=1
        else:
            remaining.append({
                **oldq,
                "higher_thinking_reason":reason,
                "prior_context_note":current.get("context_note",""),
                "review_priority":"higher",
            })
    if changes:
        decision_file=w/"pass2_hard_decisions.jsonl"
        pipe.atomic_text(decision_file,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in changes))
        pipe.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(decision_file),replace=True))
    pipe.atomic_text(w/"pass2_higher_thinking_remaining.jsonl",
            "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in remaining))
    current=pipe.load_rows(w/"pass2.jsonl","candidate_id")
    summary={
        "stage":"pass2_hard_structures",
        "initial_higher_thinking_queue":len(initial),
        "newly_resolved":len(changes),
        "still_higher_thinking":len(remaining),
        "by_logical_form":dict(sorted(patterns.items())),
        "final_pass2_statuses":dict(sorted(Counter(x["context_status"] for x in current.values()).items())),
        "proofs_read":False,
        "math_validity_assessed":False,
        "confidence":"source_structure_interpretation_unverified",
        "batch":w.name,
    }
    assert len(initial)==len(changes)+len(remaining)+sum(
       existing[x]["context_status"]=="resolved" for x in initial)
    pipe.atomic_text(w/"pass2_hard_summary.json",json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workdir",required=True)
    run(p.parse_args())

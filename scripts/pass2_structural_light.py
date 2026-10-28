#!/usr/bin/env python3
"""Second, bounded Pass 2 structural pass: only prior needs_structure entries.

Preserves original statement and original classification. Extracts an explicit
top-level assumption/conclusion boundary, including \begin{enumerate} blocks,
without interpreting enumerated equivalences as one-way implications.
Anything ambiguous goes to a *separate* higher-thinking Pass 2 queue.
Proofs are NEVER opened; no mathematical truth claims are made.
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

ENUM_OPEN=re.compile(r"\\begin\{enumerate\}")
ENUM_CLOSE=re.compile(r"\\end\{enumerate\}")
THEN=re.compile(r"\bthen\b",re.I)
INTRO=re.compile(r"^(?:Let|Suppose|Assume|Fix|Given|Consider|For)\b",re.I)
EQUIV=re.compile(r"\b(?:following|these|those)\s+(?:conditions|statements|assertions|properties)?\s*(?:are|is)\s+equivalent\b|\bif\s+and\s+only\s+if\b",re.I)
UNBOUND=re.compile(r"\b(?:above|preceding|previously|earlier|as\s+in|situation)\b",re.I)
MULTI_CASE=re.compile(r"\\item\b|\\begin\{(?:itemize|description)\}",re.I)

def math_spans(s):
    """Cheap TeX inline/display math masking; never split within $...$."""
    result=[]
    for m in re.finditer(r"(?<!\\)\$\$[\s\S]*?(?<!\\)\$\$|(?<!\\)\$[^\$]*?(?<!\\)\$",s):
        result.append((m.start(),m.end()))
    return result

def protected(pos,intervals):
    return any(a<=pos<b for a,b in intervals)

def top_level_enumerations(s):
    stack=[]
    blocks=[]
    for m in re.finditer(r"\\(?:begin|end)\{enumerate\}",s):
        if m.group().startswith("\\begin"):
            stack.append(m.start())
        else:
            if not stack:
                return None
            begin=stack.pop()
            if not stack:
                blocks.append((begin,m.end()))
    return blocks if not stack else None

def split(s):
    """Return (hypothesis text, conclusion text, reason) or (None,None,reason)."""
    text=s.strip()
    if not text:
        return None,None,"empty statement"
    if UNBOUND.search(text):
        return None,None,"possible inherited notation or context"
    if EQUIV.search(text):
        return None,None,"equivalence requires bidirectional interpretation"
    blocks=top_level_enumerations(text)
    if blocks is None:
        return None,None,"unbalanced enumerated environments"
    # Top-level 'Then' outside displayed mathematics, even when a condition
    # or conclusion contains enumerate or diagrams.
    spans=math_spans(text)
    candidates=[m for m in THEN.finditer(text) if not protected(m.start(),spans)]
    for m in candidates:
        left,right=text[:m.start()].strip(),text[m.end():].strip()
        if not left or not right:
            continue
        if not INTRO.match(left) and not re.search(r"(?<![A-Za-z])(?:if|assume|suppose|whenever|provided)\b",left,re.I):
            continue
        if any(a<m.start()<b for a,b in blocks):
            continue
        if text.count("$$")%2:
            return None,None,"unbalanced displayed mathematics"
        return left,right,"explicit top-level THEN boundary"
    # If a statement's outer enumerate is preceded by assumptions and is
    # followed by no further assertion, the list usually contains conclusions
    # only. Restrict to source-native setup/statement grammar.
    if len(blocks)==1:
        a,b=blocks[0]
        prefix=text[:a].strip()
        suffix=text[b:].strip(" .\n\t")
        if prefix and INTRO.match(prefix) and not suffix:
            if re.search(r"\b(?:Assume|Suppose|Let|Given|such\s+that|if|conditions?)\s*$",prefix,re.I):
                return None,None,"enumeration may list assumptions"
            if re.search(r"\b(?:following|these)\s+(?:are|is)\b",prefix,re.I):
                return None,None,"ambiguous list direction"
            if re.search(r"\b(?:Then|We\s+have|The\s+following\s+hold)\b",prefix,re.I):
                boundary=re.search(r"\b(?:Then|We\s+have|The\s+following\s+hold)\b",prefix,re.I)
                left=prefix[:boundary.start()].strip()
                right=prefix[boundary.end():].strip()+"\n"+text[a:b]
                if left and right.strip():
                    return left,right.strip(),"explicit result enumeration"
    # Unenumerated sentences following source-native Let/Assume clauses.
    # The first 'Let' may be a multi-line environment; find a later sentence
    # that starts with a clear existential/universal assertion.
    if not blocks and INTRO.match(text):
        for m in re.finditer(r"\.\s+(?=(?:There\s+(?:is|are|exists?)|"
                              r"The\s+(?:map|morphism|functor|object|natural|induced)|"
                              r"Every|Any|For\s+every|We\s+have|It\s+follows|"
                              r"The\s+following)\b)",text,re.I):
            left,right=text[:m.start()+1].strip(),text[m.end():].strip()
            if left and right:
                return left,right,"statement after introductory assumptions"
    return None,None,"requires semantic interpretation of structure"

def run(args):
    w=Path(args.workdir)
    existing=pipe.load_rows(w/"pass2.jsonl","candidate_id")
    raw=pipe.load_rows(w/"pass1.jsonl","candidate_id")
    target={k:v for k,v in existing.items() if v["context_status"]=="needs_structure"}
    updated=[]
    higher=[]
    for ident,p2 in sorted(target.items()):
        s=p2["statement"]
        h,c,reason=split(s)
        if h and c:
            if not (h in s and c in s):
                raise AssertionError(f"source span not preserved for {ident}")
            updated.append({
                **p2,"hypotheses":[h],"conclusions":[c],
                "context_status":"resolved","context_note":"",
                "review_method":"mechanical_syntax",
                "split_confidence":"structural_syntax_only",
                "statement_editorial_notes":"Bounded structural Pass 2: "+reason+
                    ". Source spans preserved verbatim. Requires editorial QA; no proof review.",
            })
        else:
            higher.append({
                "candidate_id":ident,
                "source_url":raw[ident]["source"]["source_url"],
                "statement_tex":raw[ident]["statement_tex"],
                "statement":s,"reason":reason,
                "source_file":raw[ident]["source"]["filename"],
                "entry_type":raw[ident]["entry_type"],
                "queue":"pass2_higher_thinking",
                "proofs_read":False,
            })
    # Atomic stage apply uses existing structural state rules.
    if updated:
        decisions_file=w/"pass2_structural_decisions.jsonl"
        pipe.atomic_text(decisions_file,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in updated))
        pipe.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(decisions_file),replace=True))
    pipe.atomic_text(w/"pass2_higher_thinking.jsonl","".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in higher))
    final=pipe.load_rows(w/"pass2.jsonl","candidate_id")
    report={"target_before":len(target),"split_now":len(updated),
        "needs_higher_thinking":len(higher),
        "current_statuses":dict(sorted(Counter(p["context_status"] for p in final.values()).items())),
        "stage":"pass2_structural_light","proofs_read":False,
        "review_method":"source-faithful bounded syntactic split, NOT semantic verification",
        "batch":w.name}
    assert len(updated)+len(higher)==len(target)
    pipe.atomic_text(w/"pass2_structural_summary.json",json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--workdir",required=True)
    run(p.parse_args())

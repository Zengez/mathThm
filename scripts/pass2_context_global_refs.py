#!/usr/bin/env python3
"""Pass 2: recover uniquely pinned cross-file named source context (statements only).

Restrict promotion to canonical needs_context entries with an explicit, uniquely
located source label and a source-faithful grammatical hypotheses/conclusions
split. Notation / definitions are background; never silently make a referenced
lemma's result a hypothesis. Do not read proof blocks or publish theorem data.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.pass2_context_source_probe import get_index,BATCHES
from scripts.pass2_remaining_targeted import source_body
from scripts.pass2_context_secondary import parse_statement
from scripts.pass2_pinned_named_reference import source_grammar
from scripts.pass2_hard_structures import safe_setup,mask_math,enum_blocks

CITE=re.compile(
    r"(?i)\b(?:in\s+(?:the\s+)?(?:situation|setting)\s+(?:of\s+)?|"
    r"(?:as|defined|described|introduced|constructed)\s+in\s+|"
    r"(?:as|from|of)\s+|(?:with|under)\s+(?:the\s+)?(?:notation|assumptions)\s+(?:as\s+in|of|from)\s+)"
    r"(?:[A-Z][A-Za-z\s]{0,45},\s*)?"
    r"(?:Situation|Definition|Remark|Lemma|Proposition|Theorem|Notation|Setup|Construction|Convention)"
    r"\s*\\ref\{(?P<label>[^{}]+)\}")
BARE_HEADER=re.compile(
    r"(?is)^(?:Assumptions\s+and\s+notation|Notation\s+and\s+assumptions|"
    r"With\s+(?:the\s+)?notation|With\s+(?:the\s+)?assumptions)"
    r"\s+as\s+in\s+(?:[A-Za-z\s]+,\s*)?"
    r"(?:Lemma|Definition|Remark|Situation|Theorem|Proposition)"
    r"\s*\\ref\{[^{}]+\}\s*[.:,;]\s*")
SITUATION_HEADER=re.compile(
    r"(?is)^(?:In|Under)\s+(?:the\s+)?(?:Situation|Setup|Notation)\s*"
    r"\\ref\{[^{}]+\}\s*[,.:;]?\s*")
CONTEXT_EXTRAS=re.compile(
    r"(?i)\b(?:as\s+above|as\s+before|notation\s+as\s+above|"
    r"in\s+the\s+situation\s+(?:above|below)|as\s+defined\s+above|"
    r"as\s+in\s+the\s+previous|as\s+constructed\s+above)\b")
CLAIM_START=re.compile(
    r"(?i)^(?:There|The|This|These|It|We|For|Every|Each|Any|"
    r"An|A|One|Then|Hence|Therefore|In\s+(?:this|the)\b)")
OPEN_END=re.compile(r"(?i)\b(?:if|then|and|or|such\s+that|whenever)\s*$")
EXTRA_CLAUSES=re.compile(r"(?i)\b(?:conversely|if\s+and\s+only\s+if|"
    r"the\s+following\s+(?:are|is)\s+equivalent)\b")
REV="a04446e57ec1fbc252a871afcec7752fb2807b14"

def source_refs(body):
    # Exact explicit citations only. Equations and section pointers are not
    # standing-assumption environments and need a different review.
    return list(dict.fromkeys(m.group("label") for m in CITE.finditer(body)))

def parse_remainder(body):
    # Existing source/grammar interpreters retain enumerated equivalences.
    for fn in (source_grammar,parse_statement):
        try:
            out,why=fn(body)
            if out and out.get("hypotheses") and out.get("conclusions"):
                return out,"grammar: "+str(why)
        except (ValueError,KeyError,IndexError,TypeError):
            pass
    split=safe_setup(body)
    if split and all(split):
        return {"hypotheses":[split[0]],"conclusions":[split[1]],
                "logical_form":"source_setup_assertion",
                "equivalence_sides":[],"structured_cases":[]},"explicit Let/setup preceding assertion"
    return None,"no safe source grammatical split"

def parse_header_claim(body):
    # Only after a distinct, exact source header; the *cited* context then
    # supplies the hypotheses. No invented empty premise.
    header=BARE_HEADER.match(body) or SITUATION_HEADER.match(body)
    if not header:return None,"no exact cited-context header"
    rest=body[header.end():].strip()
    if not rest:return None,"empty result after context"
    logical,why=parse_remainder(rest)
    if logical:return logical,why
    # Whole result retained; avoid ambiguous equivalences and enumerations.
    if (CLAIM_START.match(rest) and len(rest)<=1800
        and not EXTRA_CLAUSES.search(mask_math(rest))
        and enum_blocks(rest)==[] and not OPEN_END.search(rest)):
        # Additional "if ... then" inside must have a safe split; never
        # silently label a conditional as a plain assertion.
        if not re.search(r"\bif\b",mask_math(rest),re.I):
            return {"hypotheses":[],"conclusions":[rest],
                    "logical_form":"assertion_under_exact_cited_context",
                    "equivalence_sides":[],"structured_cases":[]},"full source assertion under exact context"
    return None,"remaining clause is logically complex"

def index_sources(root):
    all_files=[q for q in root.rglob("*.tex") if q.is_file()]
    # Use the same bounded non-proof-environment extractor as previous passes.
    allindex=get_index(root,[str(q.relative_to(root)) for q in all_files])
    by_label=defaultdict(list)
    for (filename,label),entry in allindex.items():
        by_label[label].append((filename,entry))
    return by_label,len(all_files)

def interpret(base,raw,index):
    body,_=source_body(base["statement"])
    if CONTEXT_EXTRAS.search(body):
        return None,"unexpanded unlabelled previous context"
    refs=source_refs(body)
    if not refs:return None,"no explicit named inherited context label"
    if len(refs)>3:return None,"more than three context references"
    fn=raw["source"]["filename"]
    revision=raw["source"]["revision"]
    src_line=raw["source"]["statement_line"]
    if revision!=REV:return None,"unexpected source revision"
    extracted=[]
    for label in refs:
        matches=index.get(label,[])
        if len(matches)!=1:return None,"reference label absent or non-unique globally"
        filename,ref=matches[0]
        if filename==fn and ref["line"]>=src_line:
            return None,"cited statement not earlier in same file"
        if ref["kind"].lower() not in (
            "situation","notation","setup","definition","remark",
            "construction","convention","lemma","proposition","theorem"):
            return None,"unsupported context entity"
        text=ref["text"]
        if not 15<=len(text)<=2600:return None,"context source too short/long"
        # All context recorded verbatim with precise path/revision.
        extracted.append({
            "label":label,"kind":ref["kind"],"filename":filename,
            "statement_line":ref["line"],"source_revision":revision,
            "source_statement":text})
    out,why=parse_remainder(body)
    method="full_statement_explicit_grammar"
    if not out:
        out,why=parse_header_claim(body)
        method="exact_header_and_source_assertion"
    if not out:return None,why
    h=list(out.get("hypotheses",[]))
    c=list(out.get("conclusions",[]))
    if not c:return None,"missing result"
    # Referenced definitions are terminology; original conditions and the
    # exact context header are retained. If no independent local premises
    # exist, use only a matched exact standing-context header, never a
    # referenced theorem's mathematical conclusion as a premise.
    if not h:
        header=BARE_HEADER.match(body) or SITUATION_HEADER.match(body)
        if not header:return None,"no literal cited setup for standalone assertion"
        h=[body[:header.end()].strip()]
    if not h:return None,"missing explicit source context"
    return {
        **base,"hypotheses":h,"conclusions":c,
        "context_status":"resolved","context_note":"",
        "logical_form":out.get("logical_form","source_statement"),
        "equivalence_sides":out.get("equivalence_sides",[]),
        "structured_cases":out.get("structured_cases",[]),
        "local_context_used":extracted,
        "review_method":"editorial",
        "split_confidence":"pinned_global_reference_source_grammar_unverified",
        "statement_editorial_notes":
            "Pass 2 exact globally unique reference, "+method+"; "+why+
            ". Cited source environments recorded as context, not as new "+
            "mathematical hypotheses. Source is pinned; no proof reading or validation."
    },"resolved"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",default="upstream/stacks")
    args=ap.parse_args()
    index,scanned=index_sources(Path(args.source_root))
    rollup=Counter()
    summaries=[]
    for name in BATCHES:
        w=Path("harvest/batches")/name
        raw=p.load_rows(w/"pass1.jsonl","candidate_id")
        current=p.load_rows(w/"pass2.jsonl","candidate_id")
        before=Counter(x["context_status"] for x in current.values())
        changed=[];deferred=Counter()
        for ident,entry in sorted(current.items()):
            if entry["context_status"]!="needs_context":continue
            updated,reason=interpret(entry,raw[ident],index)
            if updated:changed.append(updated)
            else:deferred[reason]+=1
        if changed:
            decisions=w/"pass2_context_global_reference_decisions.jsonl"
            p.atomic_text(decisions,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in changed))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(decisions),replace=True))
        after=p.load_rows(w/"pass2.jsonl","candidate_id")
        assert set(raw)==set(after)
        counts=Counter(x["context_status"] for x in after.values())
        assert before["needs_context"]-counts["needs_context"]==len(changed)
        assert all(v["hypotheses"] and v["conclusions"] for v in after.values() if v["context_status"]=="resolved")
        assert not p.load_rows(w/"pass3.jsonl","candidate_id")
        summary={"batch":name,"before_context":before["needs_context"],
            "newly_resolved":len(changed),"after_context":counts["needs_context"],
            "remaining_reasons":dict(sorted(deferred.items())),
            "statuses_after":dict(sorted(counts.items())),
            "proofs_read":False,"math_validity_audited":False}
        p.atomic_text(w/"pass2_context_global_reference_summary.json",
                      json.dumps(summary,indent=2,sort_keys=True)+"\n")
        summaries.append(summary)
        rollup.update(counts)
    assert sum(rollup.values())==10987
    out={"source_revision":REV,"source_tex_files_scanned":scanned,
         "globally_indexed_labels":len(index),"batches":summaries,
         "status_totals":dict(sorted(rollup.items())),
         "new_context_resolutions":sum(s["newly_resolved"] for s in summaries),
         "proofs_read":False,"pass3_started":False,"public_catalog_unchanged":True}
    p.atomic_text(Path("harvest/PASS2_CONTEXT_GLOBAL_REPORT_2026-10-28.json"),
                 json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":main()

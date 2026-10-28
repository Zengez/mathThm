#!/usr/bin/env python3
"""Recover source-specific Stacks notation-section standing context for Pass 2.

Only tightly scoped 'as in Section \\ref{section-notation...}' citations,
with exact named section preamble text in the same pinned source file. Refuse
long sections, cross-chapter citations and ambiguous multi-context statements.
No proofs read, no theorem validation.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from collections import Counter
from . import harvest_pipeline as p
from .pass2_context_source_probe import BATCHES
from .pass2_pinned_named_reference import source_grammar
from .pass2_remaining_targeted import source_body

HEADING=re.compile(r"\\section\{(?P<title>[^{}\n]+)\}\s*\\label\{(?P<label>section-[^{}\n]+)\}")
CUTOFF=re.compile(r"\\(?:section|subsection)\{|\\begin\{(?:lemma|proposition|theorem|corollary|definition|example|remark|proof)\}",re.I)
SECREF=re.compile(r"\b(?:as|from|of|in)\s+(?:the\s+)?Section\s*\\ref\{(?P<label>section-[^{}]+)\}",re.I)
QUAL=re.compile(r"^(?:section-(?:notation|conventions(?:-notation)?|setup|preliminaries))$",re.I)
INTRO=re.compile(r"(?i)(?:^|\n)(?:\\noindent\s*)?(?:Let|Fix|Throughout|We\s+(?:fix|assume)|In\s+this\s+(?:section|chapter))\b")
UNSAFE=re.compile(r"(?i)\b(?:as\s+above|in\s+the\s+situation\s+above|"
                  r"with\s+(?:the\s+)?notation\s+as\s+in\s+(?:Lemma|Theorem)|"
                  r"assumptions\s+and\s+notation\s+as\s+in\s+(?:Lemma|Theorem))\b")

def index_section_text(root,files):
    output={}
    for filename in sorted(files):
        path=root/filename
        if not path.is_file():continue
        s=path.read_text(encoding="utf-8")
        for m in HEADING.finditer(s):
            after=s[m.end():]
            cut=CUTOFF.search(after)
            text=after[:cut.start() if cut else min(len(after),6000)].strip()
            # Remove stand-alone comments but preserve mathematical source.
            text=re.sub(r"(?m)^%[^\n]*\n","",text).strip()
            output[(filename,m.group("label"))]={"title":m.group("title"),
                         "text":text,"line":s.count("\n",0,m.start())+1,
                         "complete":cut is not None}
    return output

def interpret(base,raw,sections):
    body,_=source_body(base["statement"])
    refs=list(SECREF.finditer(body[:750]))
    if len(refs)!=1:return None,"Needs exactly one explicit early Section reference"
    label=refs[0].group("label")
    if not QUAL.match(label):return None,"Section is not a known notation/setup header"
    fn=raw["source"]["filename"]
    section=sections.get((fn,label))
    if not section:return None,"Cited Section not in same source file"
    if not section["complete"] or section["line"]>=raw["source"]["statement_line"]:
        return None,"Section not earlier or not safely delimited"
    section_text=section["text"]
    if not 30<=len(section_text)<=3000 or not INTRO.search(section_text):
        return None,"Section preamble too long/short or lacks explicit standing context"
    if UNSAFE.search(body):return None,"Other unexpanded context also present"
    if len(re.findall(r"\bas\s+in\b",body,re.I))>1:
        return None,"Additional separate inherited context references"
    logical,why=source_grammar(body)
    if not logical:return None,why
    text=section["text"]
    context=[{"label":label,"kind":"section_notation_preamble","filename":fn,
              "source_revision":raw["source"]["revision"],
              "statement_line":section["line"],"source_statement":text}]
    return {**base,**logical,
         "context_status":"resolved","context_note":"",
         "review_method":"editorial",
         "split_confidence":"pinned_source_notation_section_expansion_unverified",
         "local_context_used":context,
         "statement_editorial_notes":"Pass 2 exact earlier notation-section source context included. "+
             why+". Original statement retained; no proof or mathematical validity assessment."}, "resolved"

def run(args):
    root=Path(args.source_root)
    sources={}
    allfiles=set()
    for name in BATCHES:
        w=Path("harvest/batches")/name
        raw=p.load_rows(w/"pass1.jsonl","candidate_id")
        rows=p.load_rows(w/"pass2.jsonl","candidate_id")
        sources[name]=(w,raw,rows)
        allfiles.update(v["source"]["filename"] for v in raw.values())
    sections=index_section_text(root,allfiles)
    for name,(w,raw,rows) in sources.items():
        updated=[];blocked=Counter();forms=Counter()
        for ident,v in sorted(rows.items()):
            if v["context_status"]!="needs_context":continue
            entry,reason=interpret(v,raw[ident],sections)
            if entry:
                updated.append(entry);forms[entry["logical_form"]]+=1
            else:blocked[reason]+=1
        if updated:
            file=w/"pass2_pinned_section_decisions.jsonl"
            p.atomic_text(file,"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in updated))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(file),replace=True))
        final=p.load_rows(w/"pass2.jsonl","candidate_id")
        summary={"batch":name,"newly_resolved":len(updated),"forms":dict(sorted(forms.items())),
                 "blocked":dict(sorted(blocked.items())),
                 "statuses":dict(sorted(Counter(v["context_status"] for v in final.values()).items())),
                 "no_proof_review":True}
        p.atomic_text(w/"pass2_pinned_section_summary.json",json.dumps(summary,indent=2,sort_keys=True)+"\n")
        print(json.dumps(summary,sort_keys=True))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-root",default="upstream/stacks")
    run(parser.parse_args())

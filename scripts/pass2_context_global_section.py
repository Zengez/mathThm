#!/usr/bin/env python3
"""Pass 2 inherited context: exact pinned Stacks section notation/setup headers.

Never import a section's results as theorem hypotheses. Only index source
statements with a safe logical split, after retaining the precise earlier
source section's bounded non-proof setup. Leave broad/general sections open.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from collections import defaultdict,Counter
from scripts import harvest_pipeline as p
from scripts.pass2_context_source_probe import BATCHES
from scripts.pass2_context_global_refs import parse_remainder,REV
from scripts.pass2_remaining_targeted import source_body

HEAD=re.compile(r"\\section(?:\[[^\]\n]*\])?\{(?P<title>[^{}\n]{1,150})\}\s*\\label\{(?P<label>section-[^{}\n]+)\}",re.I)
CUTOFF=re.compile(r"\\(?:section|subsection)\{|\\begin\{(?:lemma|proposition|theorem|corollary|definition|example|remark|proof|exercise)\}",re.I)
REF=re.compile(r"(?i)\b(?:as\s+in|as\s+defined\s+in|from|of|in)\s+(?:the\s+)?Section\s*\\ref\{(?P<label>section-[^{}]+)\}")
SETUP=re.compile(r"(?i)(?:^|\n)(?:\\noindent\s*)?(?:Let|Fix|Throughout|We\s+(?:fix|assume)|In\s+this\s+(?:section|chapter))\b")
OTHER=re.compile(r"(?i)\b(?:as\s+(?:above|before)|in\s+the\s+situation\s+above|"
    r"as\s+defined\s+above|with\s+notation\s+as\s+above)\b")
QUAL=re.compile(r"(?i)(?:notation|convention|setup|preliminar|introduction|constructions|definitions)")

def index(root):
    res=defaultdict(list)
    for f in sorted(root.rglob("*.tex")):
        source=f.read_text(encoding="utf-8")
        for m in HEAD.finditer(source):
            tail=source[m.end():]
            cutoff=CUTOFF.search(tail)
            if cutoff is None:continue
            pre=tail[:cutoff.start()].strip()
            pre=re.sub(r"(?m)^%[^\n]*\n","",pre).strip()
            res[m.group("label")].append({
                "file":str(f.relative_to(root)),"title":m.group("title"),
                "text":pre,"line":source.count("\n",0,m.start())+1})
    return res

def interpret(base,raw,sections):
    body,_=source_body(base["statement"])
    if OTHER.search(body):return None,"additional unlabelled prior context"
    labels=list(dict.fromkeys(m.group("label") for m in REF.finditer(body)))
    if len(labels)!=1:return None,"no single explicit Section reference"
    matches=sections.get(labels[0],[])
    if len(matches)!=1:return None,"section label missing or non-unique"
    source=matches[0]
    if raw["source"]["revision"]!=REV:return None,"source revision mismatch"
    if source["file"]==raw["source"]["filename"] and source["line"]>=raw["source"]["statement_line"]:
        return None,"later source section"
    # Unlike a definitional citation, a broad section likely supplies context
    # elsewhere, so use only tightly bounded setup sections with actual setup.
    if not QUAL.search(source["title"]+" "+labels[0]):
        return None,"broad section without explicit notation/setup scope"
    excerpt=source["text"]
    if not 20<=len(excerpt)<=2800 or not SETUP.search(excerpt):
        return None,"section standing notation absent or too long"
    out,why=parse_remainder(body)
    if not out:return None,"original theorem structure still ambiguous"
    if not out.get("hypotheses") or not out.get("conclusions"):
        return None,"no source hypothesis/result pair"
    context=[{
       "label":labels[0],"kind":"section_notation_or_setup",
       "filename":source["file"],"statement_line":source["line"],
       "source_revision":REV,"source_statement":excerpt,
       "title":source["title"]}]
    return {
        **base,"hypotheses":out["hypotheses"],"conclusions":out["conclusions"],
        "logical_form":out.get("logical_form","source_statement"),
        "equivalence_sides":out.get("equivalence_sides",[]),
        "structured_cases":out.get("structured_cases",[]),
        "context_status":"resolved","context_note":"",
        "local_context_used":context,"review_method":"editorial",
        "split_confidence":"pinned_global_section_setup_source_grammar_unverified",
        "statement_editorial_notes":
          "Pass 2: exact cited notation/setup section preamble, source pinned. "+
          str(why)+". Original theorem source and citation retained; no proof or truth audit."
    },"resolved"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",default="upstream/stacks")
    args=ap.parse_args()
    sec=index(Path(args.source_root))
    result=[];totals=Counter()
    for name in BATCHES:
        w=Path("harvest/batches")/name
        raw=p.load_rows(w/"pass1.jsonl","candidate_id")
        before=p.load_rows(w/"pass2.jsonl","candidate_id")
        previous=Counter(v["context_status"] for v in before.values())
        changes=[];reasons=Counter()
        for ident,item in sorted(before.items()):
            if item["context_status"]!="needs_context":continue
            d,why=interpret(item,raw[ident],sec)
            if d:changes.append(d)
            else:reasons[why]+=1
        if changes:
            path=w/"pass2_context_global_section_decisions.jsonl"
            p.atomic_text(path,"".join(json.dumps(z,sort_keys=True,ensure_ascii=False)+"\n" for z in changes))
            p.apply_pass2(argparse.Namespace(workdir=str(w),decisions=str(path),replace=True))
        after=p.load_rows(w/"pass2.jsonl","candidate_id")
        counts=Counter(v["context_status"] for v in after.values())
        assert set(after)==set(before)
        assert previous["needs_context"]-counts["needs_context"]==len(changes)
        assert not p.load_rows(w/"pass3.jsonl","candidate_id")
        result.append({"batch":name,"new_resolved":len(changes),
                       "context_before":previous["needs_context"],
                       "context_after":counts["needs_context"],
                       "deferred_reasons":dict(reasons)})
        totals.update(counts)
    out={"indexed_section_labels":len(sec),"batches":result,
         "status_totals":dict(sorted(totals.items())),
         "new_context_resolved":sum(x["new_resolved"] for x in result),
         "proofs_read":False,"public_catalog_unchanged":True}
    assert sum(totals.values())==10987
    p.atomic_text(Path("harvest/PASS2_CONTEXT_SECTION_FOLLOWUP_2026-10-28.json"),
                  json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps(out,sort_keys=True,indent=2))

if __name__=="__main__":main()

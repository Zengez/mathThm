#!/usr/bin/env python3
"""Read named SAME-SOURCE Stacks statements, not proof text, to gauge Pass 2 context recovery.

This script outputs only bounded review excerpts and summary counts.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from collections import Counter,defaultdict
from scripts import harvest_pipeline as pipe

BATCHES=("stacks-bulk-2026-10-28","stacks-second-2026-10-28","stacks-remaining-2026-10-28")
LABEL=re.compile(r"\\label\{([^}]+)\}")
BEGIN=re.compile(r"\\begin\{(situation|notation|setup|lemma|definition|remark|construction|convention|theorem|proposition|corollary)\}",re.I)
SUFFIX=lambda name: re.sub(r"^.*?(?:situation|lemma|definition|notation|setup)-","",name)
def get_index(root,files):
    index={}
    for filename in files:
        path=root/filename
        if not path.exists():continue
        s=path.read_text(encoding="utf-8")
        # A bounded grammar only reads statement environments; no proof
        # environment is selected or returned.
        pat=re.compile(r"\\begin\{(situation|notation|setup|lemma|definition|remark|construction|convention|theorem|proposition|corollary)\}(?:\[[^\]\n]*\])?([\s\S]*?)\\end\{\1\}",re.I)
        for m in pat.finditer(s):
            inside=m.group(2)
            k=LABEL.search(inside[:350])
            if not k:continue
            label=k.group(1)
            index[(filename,label)]={"kind":m.group(1),"text":LABEL.sub("",inside).strip(),
                                     "file":filename,"line":s.count("\n",0,m.start())+1}
    return index

def main():
    root=Path("upstream/stacks")
    batches={}
    files=set()
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        raw=pipe.load_rows(w/"pass1.jsonl","candidate_id")
        p2=pipe.load_rows(w/"pass2.jsonl","candidate_id")
        items={ident:(raw[ident],p2[ident]) for ident in raw
               if p2[ident]["context_status"]=="needs_context"}
        batches[batch]=items
        files.update(raw[x]["source"]["filename"] for x in items)
    idx=get_index(root,files)
    counts={}
    examples={}
    for batch,items in batches.items():
        cs=Counter()
        sample=defaultdict(list)
        for ident,(r,p2) in sorted(items.items()):
            refs=r.get("detected_local_references",[])
            fn=r["source"]["filename"]
            matching=[(label,idx[(fn,label)]) for label in refs if (fn,label) in idx]
            situations=[(l,v) for l,v in matching if v["kind"] in ("situation","notation","setup")]
            if not refs: k="no_labeled_reference"
            elif not matching:k="no_same_file_statement_label"
            elif situations:k="situation_notation_or_setup_available"
            else:k="other_statement_label_available"
            cs[k]+=1
            if len(sample[k])<12:
                sample[k].append({"id":ident,"statement":p2["statement"][:1100],
                          "refs":refs[:7],"matches":[{"label":l,"kind":v["kind"],
                          "length":len(v["text"]),"text":v["text"][:1800]} for l,v in matching[:2]]})
        counts[batch]=dict(sorted(cs.items()))
        examples[batch]=dict(sample)
    output={"count_by_batch":counts,"examples":examples,
            "exact_label_hits":len(idx),"files_scanned":len(files),
            "revision":"a04446e57ec1fbc252a871afcec7752fb2807b14",
            "proofs_read_or_scanned":False}
    pipe.atomic_text(Path("harvest/PASS2_CONTEXT_SOURCE_PROBE_2026-10-28.json"),
                      json.dumps(output,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"count_by_batch":counts,"exact_label_hits":len(idx),"files_scanned":len(files)}))

if __name__=="__main__":main()

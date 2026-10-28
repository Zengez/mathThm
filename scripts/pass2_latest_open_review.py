#!/usr/bin/env python3
"""Identify the actual remaining Pass 2 blockers after bounded prior reviews."""
import json,re
from pathlib import Path
from collections import Counter,defaultdict
from scripts import harvest_pipeline as p
from scripts.pass2_fast_stacks import CONTEXT_DEPENDENCY

BATCHES=("stacks-bulk-2026-10-28","stacks-second-2026-10-28","stacks-remaining-2026-10-28")
CATS={
    "explicit_situation":r"\bIn\s+Situation\s+\\ref\{",
    "standalone_above":r"\b(?:as\s+above|in\s+the\s+situation\s+above|defined\s+above)\b",
    "lemma_context":r"\b(?:Assumptions\s+and\s+notation\s+as\s+in\s+Lemma|With\s+notation\s+as\s+in\s+Lemma)\b",
    "definition_reference":r"\bas\s+in\s+(?:Definition|Remark)\s+\\ref\{",
    "section_reference":r"\bas\s+in\s+Section\s+\\ref\{",
    "source_internal_diagram":r"\bthe\s+following\s+diagram\b",
    "source_metadata":r"^\s*\\begin\{reference\}",
    "as_in_general":r"\bas\s+in\b",
}
def main():
    output={}
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        raw=p.load_rows(w/"pass1.jsonl","candidate_id")
        dec=p.load_rows(w/"pass2.jsonl","candidate_id")
        context_groups=Counter(); examples=defaultdict(list)
        hard_groups=Counter(); hardexamples=defaultdict(list)
        questionable=[]
        for ident,d in sorted(dec.items()):
            s=d["statement"]
            if d["context_status"]=="needs_classification":
                questionable.append({"id":ident,"statement":s[:2300],
                    "entry_type":raw[ident]["entry_type"],
                    "source_label":raw[ident]["source"]["label"],
                    "source_file":raw[ident]["source"]["filename"],
                    "context_note":d["context_note"]})
            elif d["context_status"]=="needs_context":
                found=[k for k,regex in CATS.items() if re.search(regex,s,re.I)]
                key=found[0] if found else "uncategorized_context"
                context_groups[key]+=1
                if len(examples[key])<15:
                    examples[key].append({"id":ident,"statement":s[:950],
                        "ref_count":len(raw[ident].get("detected_local_references",[])),
                        "first_refs":raw[ident].get("detected_local_references",[])[:3]})
            elif d["context_status"]=="needs_structure":
                key=("enumerate" if "\\begin{enumerate}" in s else
                     "reference_preamble" if s.startswith("\\begin{reference}") else
                     "iff" if "if and only if" in s else
                     "conditional" if re.search(r"\bif\b",s,re.I) else
                     "unconditional")
                hard_groups[key]+=1
                if len(hardexamples[key])<20:
                    hardexamples[key].append({"id":ident,"statement":s[:1200]})
        output[batch]={"statuses":dict(sorted(Counter(d["context_status"] for d in dec.values()).items())),
            "context_groups":dict(sorted(context_groups.items())),
            "context_examples":dict(examples),
            "hard_groups":dict(sorted(hard_groups.items())),
            "hard_examples":dict(hardexamples),
            "classification_cases":questionable}
    p.atomic_text(Path("harvest/PASS2_LATEST_OPEN_REVIEW_2026-10-28.json"),
                  json.dumps(output,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print(json.dumps({k:{name:row[name] for name in ('statuses','context_groups','hard_groups','classification_cases')}
        for k,row in output.items()},indent=2))

if __name__=="__main__": main()

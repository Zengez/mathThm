#!/usr/bin/env python3
"""Read-only Pass 2 inventory: group source-context triggers and hard forms.

No proof parsing, decision changes or mathematical validation.
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

try:
    from scripts import harvest_pipeline as p
    from scripts.pass2_fast_stacks import CONTEXT_DEPENDENCY
except ImportError:
    import harvest_pipeline as p
    from pass2_fast_stacks import CONTEXT_DEPENDENCY

BATCHES=("stacks-bulk-2026-10-28","stacks-second-2026-10-28","stacks-remaining-2026-10-28")

def trigger_category(s):
    hits=list(CONTEXT_DEPENDENCY.finditer(s))
    if not hits:return "unmatched_source_context_detector",[]
    desc=[]
    for h in hits:
        desc.append({"matched":h.group(),"excerpt":s[max(0,h.start()-70):min(len(s),h.end()+120)].replace("\n"," ")})
    lower=hits[0].group().lower()
    if "construction" in lower or "diagram" in lower or "data" in lower:return "dependent_construction",desc
    if "situation" in lower or "setup" in lower:return "standing_situation",desc
    if "notation" in lower or "assumptions" in lower or "hypotheses" in lower:return "notation_or_hypotheses",desc
    if "as in" in lower:return "citation_as_in",desc
    if "above" in lower or "earlier" in lower or "previous" in lower:return "reference_to_prior",desc
    return "other",desc

def run():
    stats={}
    for batch in BATCHES:
        wd=Path("harvest/batches")/batch
        raw=p.load_rows(wd/"pass1.jsonl","candidate_id")
        current=p.load_rows(wd/"pass2.jsonl","candidate_id")
        cgroups=Counter(); examples=defaultdict(list)
        refs=Counter(); context_reasons=Counter()
        for ident,v in sorted(current.items()):
            if v["context_status"]!="needs_context":continue
            s=v["statement"]
            group,hits=trigger_category(s)
            cgroups[group]+=1
            refs[str(min(len(raw[ident].get("detected_local_references",[])),5))]+=1
            context_reasons[v["context_note"]]+=1
            if len(examples[group])<18:
                examples[group].append({
                    "id":ident,"source_file":raw[ident]["source"]["filename"],
                    "statement":s[:1200],
                    "local_refs":raw[ident].get("detected_local_references",[])[:10],
                    "matches":hits[:5],
                })
        hard=defaultdict(list)
        for ident,v in sorted(current.items()):
            if v["context_status"]!="needs_structure":continue
            s=v["statement"]
            typ=("source_reference_prefix" if s.startswith("\\begin{reference}") else
                 "enumeration" if "\\begin{enumerate}" in s else
                 "unlisted_biconditional" if "if and only if" in s else
                 "explicit_if" if re.search(r"\bif\b",s,re.I) else
                 "unconditional_or_other")
            if len(hard[typ])<15:
                hard[typ].append({"id":ident,"statement":s[:1000],"file":raw[ident]["source"]["filename"]})
        stats[batch]={
            "total":len(raw),
            "statuses":dict(sorted(Counter(v["context_status"] for v in current.values()).items())),
            "source_revisions":dict(sorted(Counter(v["source"]["revision"] for v in raw.values()).items())),
            "context_groups":dict(sorted(cgroups.items())),
            "context_refs_count":dict(sorted(refs.items())),
            "context_notes":dict(sorted(context_reasons.items())),
            "context_examples":dict(examples),
            "hard_examples":dict(hard),
        }
    dest=Path("harvest/PASS2_OPEN_DIAGNOSTICS_2026-10-28.json")
    p.atomic_text(dest,json.dumps(stats,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print(json.dumps({k:{x:v[x] for x in ("total","statuses","context_groups","context_refs_count","source_revisions")} for k,v in stats.items()},indent=2))

if __name__=="__main__":run()

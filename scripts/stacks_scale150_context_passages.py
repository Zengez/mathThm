#!/usr/bin/env python3
"""Extract bounded local definition and non-proof prose passages from current 19 sections.

Only source-local excerpts needed to understand the 150 candidates; does not
read proofs or follow references recursively, and does not infer hypotheses.
"""
from __future__ import annotations
import json,re
from pathlib import Path
from scripts import harvest_pipeline as hp
from scripts.stacks_context_recon import REV
ROOT=Path("harvest/section_walk_scale150_2026-10-28")
PAT=re.compile(r"\\begin\{(definition|situation|notation|setup|construction)\}")
CLOSE=re.compile(r"\\end\{(definition|situation|notation|setup|construction)\}")
LABEL=re.compile(r"\\label\{([^}]+)\}")
SOURCE="algebra.tex"
def main():
    m=json.loads((ROOT/"MANIFEST.json").read_text())
    lines=(Path("upstream/stacks")/SOURCE).read_text(encoding="utf-8").splitlines()
    out=[]
    for s in m["section_inventory"]:
        a,b=s["source_start_line"],s["source_end_line"]
        st=None
        text=[]
        for lineno in range(a,b+1):
            line=lines[lineno-1]
            begin=PAT.search(line)
            end=CLOSE.search(line)
            if begin and st is None:
                st=(lineno,begin.group(1))
                text=[line]
            elif st:
                text.append(line)
            if end and st:
                if st[1]!=end.group(1):raise ValueError("Unbalanced source")
                src="\n".join(text)
                label=LABEL.search(src)
                out.append({
                    "schema":"maththm.section-specific-named-context.v1",
                    "section_key":s["key"],
                    "source_revision":REV,
                    "kind":st[1],
                    "source_start_line":st[0],
                    "source_end_line":lineno,
                    "label":label.group(1) if label else None,
                    "source_url":f"https://github.com/stacks/stacks-project/blob/{REV}/{SOURCE}#L{st[0]}-L{lineno}",
                    "source_tex_excerpt":src[:3800],
                    "source_excerpt_truncated":len(src)>3800,
                    "available_as_definition_not_assumption":True,
                    "applies_to_previous_candidates":False,
                })
                st=None
                text=[]
        if st:raise ValueError("Unclosed context env")
        for ev in hp.read_jsonl(ROOT/(s["key"]+"_events.jsonl")):
            if ev["kind"] in ("potential_durable_scope_change","local_or_unclassified_prose"):
                out.append({
                    "schema":"maththm.section-specific-prose-lead.v1",
                    "section_key":s["key"],"source_revision":REV,
                    "kind":"unadjudicated_prose",
                    "source_start_line":ev["line"],
                    "source_end_line":ev["line"],
                    "label":None,
                    "source_url":f"https://github.com/stacks/stacks-project/blob/{REV}/{SOURCE}#L{ev['line']}",
                    "source_tex_excerpt":ev["text_excerpt"],
                    "requires_scope_adjudication":True,
                    "available_as_definition_not_assumption":False,
                    "applies_to_previous_candidates":False
                })
    out.sort(key=lambda r:r["source_start_line"])
    hp.atomic_text(ROOT/"SHARED_CONTEXT_EXCERPTS.jsonl",
        "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in out))
    print(json.dumps({"sections":m["sections"],"context_passages":len(out),
        "definitions":sum(q["kind"]=="definition" for q in out),
        "prose_leads":sum(q["kind"]=="unadjudicated_prose" for q in out),
        "truncated":sum(bool(q.get("source_excerpt_truncated")) for q in out)}))
if __name__=="__main__":main()

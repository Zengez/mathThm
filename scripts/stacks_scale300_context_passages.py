#!/usr/bin/env python3
"""Extract only named source contexts and short opening passages from the
300-candidate coherent/divisors run, with exact source and scope positions.

No theorem proofs, full-chapter recursive parsing, or auto-inherited premises.
Chapter-specific assumptions are reset when crossing file boundary.
"""
from __future__ import annotations
import json,re
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as hp
from scripts.stacks_context_recon import REV

ROOT=Path("harvest/section_walk_scale300_2026-10-28")
BEGIN=re.compile(r"\\begin\{(definition|situation|notation|setup|construction)\}")
END=re.compile(r"\\end\{(definition|situation|notation|setup|construction)\}")
FORMAL_START=re.compile(r"\\begin\{(lemma|proposition|theorem|corollary|definition|situation|notation|setup|construction|remark|example|proof)\}")
LABEL=re.compile(r"\\label\{([^}]+)\}")

def main():
    manifest=json.loads((ROOT/"MANIFEST.json").read_text(encoding="utf-8"))
    source_lines={file:(Path("upstream/stacks")/file).read_text(encoding="utf-8").splitlines()
                  for file in manifest["source_chapters"]}
    contexts=[]
    openings=[]
    for s in manifest["section_inventory"]:
        first,last=s["section_start_line"],s["section_end_line"]
        filename=s["source_filename"]
        lines=source_lines[filename]
        active=None
        collected=[]
        for n in range(first,last+1):
            line=lines[n-1]
            beginning=BEGIN.search(line)
            ending=END.search(line)
            if beginning and active is None:
                active=(n,beginning.group(1))
                collected=[line]
            elif active:
                collected.append(line)
            if ending and active:
                assert ending.group(1)==active[1],(filename,n,active)
                block="\n".join(collected)
                label=LABEL.search(block)
                contexts.append({
                  "schema":"maththm.scale300.named-source-context.v1",
                  "source_revision":REV,
                  "section_key":s["key"],
                  "source_filename":filename,
                  "source_chapter_order":s["chapter_order"],
                  "source_start_line":active[0],
                  "source_end_line":n,
                  "kind":active[1],
                  "label":label.group(1) if label else None,
                  "source_url":f"https://github.com/stacks/stacks-project/blob/{REV}/{filename}#L{active[0]}-L{n}",
                  "source_tex":block,
                  "reference_available_after_source_line":n,
                  "available_as_terminology_only":True,
                  "never_import_local_definition_variables_as_theorem_premises":True,
                })
                active=None;collected=[]
        if active:raise ValueError("Unclosed source context")
        title=s["section_title"]
        opener=[]
        for n in range(first,min(last+1,first+90)):
            line=lines[n-1]
            if FORMAL_START.search(line):
                break
            opener.append(line)
        introductory="\n".join(opener)
        opening={
          "schema":"maththm.scale300.section-opening.v1",
          "source_filename":filename,
          "section_key":s["key"],"section_title":title,
          "source_section_start_line":first,
          "opening_lines_read":len(opener),
          "opening_tex":introductory[:4000],
          "opening_excerpt_truncated":len(introductory)>4000,
          "source_revision":REV,
          "not_automatically_assumed_hypothesis":True,
        }
        openings.append(opening)
        for event in hp.read_jsonl(ROOT/(s["key"]+"_events.jsonl")):
            if event["kind"] in ("potential_durable_scope_change","local_or_unclassified_prose"):
                n=event["line"]
                top=max(first,n-6)
                bottom=min(last,n+15)
                contexts.append({
                  "schema":"maththm.scale300.prose-scope-lead.v1",
                  "source_revision":REV,
                  "section_key":s["key"],"source_filename":filename,
                  "source_chapter_order":s["chapter_order"],
                  "source_start_line":n,"source_end_line":n,
                  "kind":"unadjudicated_prose",
                  "signal":event["kind"],"label":None,
                  "source_url":f"https://github.com/stacks/stacks-project/blob/{REV}/{filename}#L{n}",
                  "source_tex":"\n".join(lines[top-1:bottom]),
                  "source_neighborhood_bounds":[top,bottom],
                  "reference_available_after_source_line":None,
                  "requires_actual_scope_adjudication":True,
                  "available_as_terminology_only":False,
                })
    contexts.sort(key=lambda q:(q["source_chapter_order"],q["source_start_line"]))
    hp.atomic_text(ROOT/"SHARED_CONTEXT_EXCERPTS.jsonl",
                   "".join(json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n" for x in contexts))
    hp.atomic_text(ROOT/"SECTION_OPENINGS.jsonl",
                   "".join(json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n" for x in openings))
    summary={
        "schema":"maththm.scale300.local-context-extraction.v1",
        "source_revision":REV,
        "sections_scanned":len(openings),
        "source_context_records":len(contexts),
        "named_source_context_records":sum(q["kind"]!="unadjudicated_prose" for q in contexts),
        "named_source_definitions":sum(q["kind"]=="definition" for q in contexts),
        "prose_leads":sum(q["kind"]=="unadjudicated_prose" for q in contexts),
        "context_kinds":dict(Counter(q["kind"] for q in contexts)),
        "both_chapters_covered":{q["source_filename"] for q in openings}==set(manifest["source_chapters"]),
        "no_proof_bodies_included":True,
        "source_definition_hypotheses_auto_inherited":False,
        "source_chapter_boundary_reset":True,
    }
    hp.atomic_text(ROOT/"CONTEXT_MANIFEST.json",json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()

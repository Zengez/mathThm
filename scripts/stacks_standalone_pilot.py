#!/usr/bin/env python3
"""Build tiny context-sensitive Pass 2 standalone review pilot packets.

Source-only, deterministic, no proof or theorem verdict. Select a few
explicit-context cases plus previously provisional duplicate merges.
"""
from __future__ import annotations

import json
import re
from collections import Counter,defaultdict
from pathlib import Path

from scripts import harvest_pipeline as p
from scripts.active_candidate_pool import IDS,BATCHES
from scripts.candidate_consolidation import MERGED
from scripts.stacks_context_light_index import candidate_context_bundle,MANIFEST as INDEX_MANIFEST
from scripts.stacks_context_recon import REV

DEST=Path("harvest/standalone_context_pilot_2026-10-28_packets.jsonl")
SUMMARY=Path("harvest/standalone_context_pilot_2026-10-28_manifest.json")

TARGETS=[
    "formal-spaces","formal-defos","chow","spaces-chow",
    "stacks-morphisms","stacks-cohomology","moduli","intersection",
    "etale","varieties",
]

def score(source,pass2,chapter):
    text=source["statement_tex"]
    line=source["source"]["statement_line"]
    points=0
    refs=source.get("detected_local_references") or []
    if any("situation-" in x for x in refs):
        points+=7
    if any("section-" in x or "definition-" in x for x in refs):
        points+=3
    if re.search(r"(?i)\b(?:as\s+above|in\s+the\s+situation|with\s+the\s+notation|"
                 r"as\s+in|throughout|we\s+fix)\b",text):
        points+=4
    if 70<=len(text)<=1250:
        points+=4
    if chapter=="formal-spaces" and line>=620:
        points+=4
    if chapter=="chow" and line>=1356:
        points+=5
    if chapter=="spaces-chow" and line>=35:
        points+=5
    if chapter=="formal-defos" and line>=193:
        points+=3
    if chapter=="moduli" and line>=64:
        points+=3
    # Favor easy-to-review examples rather than research-intensive ones.
    points-=len(text)//1600
    return points

def main():
    im=json.loads(INDEX_MANIFEST.read_text())
    assert im["source_revision"]==REV
    active=p.load_rows(IDS,"candidate_id")
    assert len(active)==9675
    original={}
    structured={}
    for batch in BATCHES:
        folder=Path("harvest/batches")/batch
        for ident,item in p.load_rows(folder/"pass1.jsonl","candidate_id").items():
            if ident in original:
                raise ValueError("Duplicate candidate source ID")
            original[ident]=item
        for ident,item in p.load_rows(folder/"pass2.jsonl","candidate_id").items():
            if ident in structured:
                raise ValueError("Duplicate candidate structured ID")
            structured[ident]=item
    canonical=p.load_rows(MERGED,"canonical_candidate_id")
    assert len(canonical)==8
    chapter_ids=defaultdict(list)
    for ident in active:
        src=original[ident]
        chapter=Path(src["source"]["filename"]).stem
        chapter_ids[chapter].append(ident)
    wanted=[]
    for chapter in TARGETS:
        choices=chapter_ids.get(chapter,[])
        if not choices:
            continue
        selected=max(choices,key=lambda k:(score(original[k],structured[k],chapter),
                                         -original[k]["source"]["statement_line"],k))
        wanted.append((selected,"designated_chapter_context"))
    # Additional pre/post midchapter contrasting source conventions.
    choices=chapter_ids.get("formal-spaces",[])
    early=[k for k in choices if original[k]["source"]["statement_line"]<620]
    if early:
        chosen=max(early,key=lambda k:(score(original[k],structured[k],"formal-spaces"),
                                       -original[k]["source"]["statement_line"],k))
        wanted.append((chosen,"before_formal_spaces_midchapter_convention"))
    for ident,c in sorted(canonical.items(),key=lambda kv:kv[1]["merge_group"]):
        wanted.append((ident,"provisionally_merged_group_"+str(c["merge_group"])))
    results=[]
    seen=set()
    for ident,selection in wanted:
        if ident in seen:
            continue
        seen.add(ident)
        a=original[ident]
        b=structured[ident]
        info=a["source"]
        refs=a.get("detected_local_references",[])
        bundle=candidate_context_bundle(info["filename"],info["statement_line"],refs)
        if bundle["status"]!="lookup_leads_only":
            raise ValueError(f"Unindexed candidate chapter: {ident}")
        merge=canonical.get(ident)
        context=[
            {"context_id":r["context_id"],"summary":r["review_summary"],
             "scope":r["scope_assessment"],"guards":r["guards"],
             "inherit_ids":r["inherit_context_ids"],"source_url":r["source_url"]}
            for r in bundle["standing_convention_leads"]
            if r["scope_assessment"]!="global" or r["context_id"]=="conventions:section-algebra"
        ]
        section=bundle["current_section_opening"]
        intro=bundle["chapter_introduction_opening"]
        result={
            "candidate_id":ident,"selection_reason":selection,
            "source_revision":REV,"source_filename":info["filename"],
            "source_statement_line":info["statement_line"],
            "source_url":info["source_url"],
            "source_label":info.get("label"),
            "pass2_statement":b["statement"][:2300],
            "pass2_statement_truncated":len(b["statement"])>2300,
            "pass1_statement":a["statement_tex"][:2300],
            "pass1_statement_truncated":len(a["statement_tex"])>2300,
            "pass2_hypotheses":[x[:900] for x in b["hypotheses"][:8]],
            "pass2_conclusions":[x[:900] for x in b["conclusions"][:8]],
            "pass2_hypotheses_total":len(b["hypotheses"]),
            "pass2_conclusions_total":len(b["conclusions"]),
            "pass2_logical_form":b.get("logical_form"),
            "pass2_context_status":b["context_status"],
            "pass2_local_context_used":b.get("local_context_used",[])[:3],
            "chapter_intro":{
                "section_url":intro["source_url"],
                "preview":intro["opening_preview"][:650],
                "preview_truncated":intro["preview_truncated"],
            } if intro else None,
            "current_section":{
                "title":section["section_title"],
                "label":section["section_label"],
                "start":section["section_start_line"],
                "source_url":section["source_url"],
                "opening_preview":section["opening_preview"][:1100],
                "preview_truncated":section["preview_truncated"],
            } if section else None,
            "direct_reference_leads":bundle["explicit_label_references"],
            "context_leads":context,
            "merge_group":merge["merge_group"] if merge else None,
            "merged_original_ids":merge["member_candidate_ids"] if merge else [ident],
            "merge_source_references":[
                {"candidate_id":r["candidate_id"],"source_filename":r["source_filename"],
                 "source_url":r["source_url"]}
                for r in merge["source_references"]
            ] if merge else [],
            "review_status":"awaits_standalone_mathematical_review",
            "hypotheses_not_modified":True,
            "source_proofs_not_read":True,
        }
        results.append(result)
    p.atomic_text(DEST,"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in results))
    manifest={
        "schema":"maththm.standalone-context-pilot.v1",
        "source_revision":REV,
        "pilot_candidates":len(results),
        "provisional_duplicate_groups_included":sum(bool(x["merge_group"]) for x in results),
        "chapters_in_sample":len({x["source_filename"] for x in results}),
        "exact_reference_leads":sum(len(x["direct_reference_leads"]) for x in results),
        "resolved_exact_reference_leads":sum(sum(y["status"]=="resolved_exact"
            for y in x["direct_reference_leads"]) for x in results),
        "source_context_lead_rows":sum(len(x["context_leads"]) for x in results),
        "pass2_candidates_modified":False,
        "semantic_standalone_reviews_complete":0,
        "proof_review_performed":False,
        "candidate_selection_policy":"One context-heavy but bounded example from each listed chapter plus all provisional merger group canonicals, with pre-midchapter formal spaces contrast",
        "selected_files":sorted({x["source_filename"] for x in results}),
    }
    p.atomic_text(SUMMARY,json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps(manifest,sort_keys=True))

if __name__=="__main__":
    main()

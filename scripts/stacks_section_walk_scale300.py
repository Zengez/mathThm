#!/usr/bin/env python3
"""Stage exactly 300 active candidates through 54 fully consecutive Stacks sections.

The chosen window is a suffix of coherent.tex followed immediately by a
prefix of divisors.tex, which are adjacent maintained Stacks chapters.
No completed section is repeated; no section, even empty, is skipped.
This is source scanning, NOT theorem equivalence or proof validation.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
from scripts import stacks_section_walk_pilot as sw
from scripts import harvest_pipeline as hp
from scripts.stacks_context_recon import REV
from scripts.stacks_consecutive_section_window150 import completed_section_starts

ROOT=Path("harvest/section_walk_scale300_2026-10-28")
CHOICE=ROOT/"CROSS_CHAPTER_SELECTION.json"
EXPECTED=300
CHAPTERS=["coherent.tex","divisors.tex"]
SECTIONS=54

def main():
    options=json.loads(CHOICE.read_text(encoding="utf-8"))
    chosen=options["top_windows"][0]
    assert chosen["source_revision"]==REV
    assert chosen["chapter_pair"]==CHAPTERS
    assert chosen["active_candidate_count"]==EXPECTED
    assert chosen["section_count"]==SECTIONS
    grouped,byfile,unmatched=sw.groups()
    assert not unmatched
    excluded=completed_section_starts()
    # An exact replay of this saved batch must remain reproducible after
    # it has been added to the cross-batch completed-section registry.
    registry=Path("harvest/SECTION_WALK_COMPLETED_SECTIONS.json")
    if registry.exists():
        previous=json.loads(registry.read_text(encoding="utf-8"))
        for prior in previous["sections"]:
            if prior.get("batch")=="scale300_2026-10-28":
                excluded.setdefault(prior["source_file"],set()).discard(prior["section_start_line"])
    actual=set()
    assert chosen["source_chapter_boundary_is_contiguous"]
    assert chosen["chapter_context_reset_required"]
    summary=[]
    event_counts=Counter()
    seen_second=False
    for i,section in enumerate(chosen["sections"],1):
        file=section["source_file"]
        assert file in CHAPTERS
        assert not seen_second or file==CHAPTERS[1]
        if file==CHAPTERS[1]:seen_second=True
        start,end=section["start"],section["end"]
        assert start not in excluded.get(file,set())
        s=next(x for x in byfile[file] if x["section_start_line"]==start)
        assert s["section_end_line"]==end
        count=len(grouped.get((file,start),[]))
        assert count==section["candidate_count"]
        suffix=f"s{i:02d}"
        prefix="SC300_"+suffix.upper()
        sw.pack(file,start,Path("upstream/stacks"),
                limit=max(24,count),output_prefix=prefix,
                group_data=(grouped,byfile,unmatched))
        triad={}
        for kind,ext in (("PACKETS","jsonl"),("EVENTS","jsonl"),("MANIFEST","json")):
            src=Path("harvest")/(prefix+"_"+kind+"_2026-10-28."+ext)
            dst=ROOT/(suffix+"_"+kind.lower()+"."+ext)
            dst.write_bytes(src.read_bytes())
            src.unlink()
            triad[kind]=dst
        packets=hp.read_jsonl(triad["PACKETS"])
        events=hp.read_jsonl(triad["EVENTS"])
        check=json.loads(triad["MANIFEST"].read_text())
        assert len(packets)==check["candidate_count"]==count
        assert sum(x["kind"]=="candidate_location" for x in events)==count
        begin=Counter(x["environment"] for x in events
                      if x["kind"]=="enter_local_environment")
        end_frames=Counter(x["environment"] for x in events
                           if x["kind"]=="exit_local_environment")
        assert begin==end_frames,(file,start,begin,end_frames)
        for r in packets:
            assert r["candidate_id"] not in actual
            assert r["source_filename"]==file
            actual.add(r["candidate_id"])
        event_counts.update(x["kind"] for x in events)
        summary.append({
            "section_index":i,"key":suffix,"source_filename":file,
            "chapter_order":s["chapter_number"],
            "section_title":s["section_title"],
            "section_label":s["section_label"],
            "section_start_line":start,
            "section_end_line":section["end"],
            "source_lines":end-start+1,
            "active_candidate_count":count,
            "all_source_formal_environments":sum(begin.values()),
            "active_candidate_environment_events":count,
            "source_lemma_environments":begin["lemma"],
            "source_proof_environments_skipped":check["event_counts"].get("proof_skipped",0),
            "named_definition_environments":begin["definition"],
            "named_situation_environments":begin["situation"],
            "scope_prose_review_leads":check["scope_review_leads"],
            "source_named_references":check["unique_explicit_refs"],
            "packets":str(triad["PACKETS"]),
            "events":str(triad["EVENTS"]),
            "scope_state_at_end":"candidate local environments closed; unreviewed durable context not auto-assumed",
            "candidate_drafts_completed":0,
        })
    assert len(actual)==EXPECTED and len(summary)==SECTIONS
    assert summary[0]["source_filename"]==CHAPTERS[0]
    assert summary[-1]["source_filename"]==CHAPTERS[1]
    for a,b in zip(summary,summary[1:]):
        if a["source_filename"]==b["source_filename"]:
            assert a["section_end_line"]+1==b["section_start_line"]
        else:
            assert a["source_filename"]==CHAPTERS[0]
            assert b["source_filename"]==CHAPTERS[1]
            assert b["section_start_line"]==byfile[CHAPTERS[1]][0]["section_start_line"]
            assert a["section_end_line"]==byfile[CHAPTERS[0]][-1]["section_end_line"]
    manifest={
        "schema":"maththm.section-walk-cross-chapter-scale300.v1",
        "source_revision":REV,
        "source_chapters":CHAPTERS,
        "chapter_order":chosen["chapter_order"],
        "chapter_boundary_policy":"reset chapter-specific standing assumptions; definitions only remain addressable as references",
        "all_chapters_adjacent_in_source_order":True,
        "all_sections_consecutive_and_complete":True,
        "sections":SECTIONS,
        "active_candidate_count":EXPECTED,
        "source_lines":sum(x["source_lines"] for x in summary),
        "candidate_ids_unique":True,
        "source_events_by_kind":dict(sorted(event_counts.items())),
        "section_inventory":summary,
        "proofs_reviewed":0,"source_context_semantically_adjudicated":False,
        "original_pass1_pass2_modified":False,
        "drafts_completed":0,
        "stage":"source_order_packets_saved",
    }
    hp.atomic_text(ROOT/"MANIFEST.json",
                   json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"chapters":CHAPTERS,
        "sections":len(summary),"active":len(actual),
        "source_lines":manifest["source_lines"],
        "section_counts":[x["active_candidate_count"] for x in summary],
        "possible_standing_context_leads":[(x["key"],x["scope_prose_review_leads"])
            for x in summary if x["scope_prose_review_leads"]]},ensure_ascii=False))
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Stage 150 active Stacks candidates in 19 CONSECUTIVE full Algebra sections.

Pinned source, section order, no proofs, no individual source-level partials.
The one empty candidate section is still traversed.
Outputs are read-only source packets; mathematical drafts are created separately.
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
from scripts import stacks_section_walk_pilot as sw
from scripts import harvest_pipeline as hp
from scripts.stacks_context_recon import REV

ROOT=Path("harvest/section_walk_scale150_2026-10-28")
FILE="algebra.tex"
START=4284
END=10036
TOTAL=150
SECTIONS=19

def main():
    data=sw.groups()
    grouped,chapters,unmatched=data
    assert not unmatched
    ordered=chapters[FILE]
    first_idx=next(i for i,s in enumerate(ordered)
                   if s["section_start_line"]==START)
    last_idx=next(i for i,s in enumerate(ordered)
                  if s["section_end_line"]==END)
    subset=ordered[first_idx:last_idx+1]
    assert len(subset)==SECTIONS
    assert subset[0]["section_start_line"]==START
    assert subset[-1]["section_end_line"]==END
    assert all(a["section_end_line"]+1==b["section_start_line"]
               for a,b in zip(subset,subset[1:]))
    observed=sum(len(grouped[(FILE,s["section_start_line"])]) for s in subset)
    assert observed==TOTAL,observed
    assert sum(not grouped[(FILE,s["section_start_line"])] for s in subset)==1
    ROOT.mkdir(parents=True,exist_ok=True)
    inventory=[]
    all_ids=set()
    events_count=Counter()
    prior_end=None
    for index,sec in enumerate(subset,1):
        start=sec["section_start_line"]
        count=len(grouped[(FILE,start)])
        assert prior_end is None or start==prior_end+1
        suffix=f"s{index:02d}"
        prefix="SC150_"+suffix.upper()
        sw.pack(FILE,start,Path("upstream/stacks"),
                limit=max(24,count),output_prefix=prefix,group_data=data)
        trio={}
        for kind,ext in (("PACKETS","jsonl"),("EVENTS","jsonl"),("MANIFEST","json")):
            src=Path("harvest")/(prefix+"_"+kind+"_2026-10-28."+ext)
            dst=ROOT/(suffix+"_"+kind.lower()+"."+ext)
            dst.write_bytes(src.read_bytes())
            src.unlink()
            trio[kind]=dst
        packets=hp.read_jsonl(trio["PACKETS"])
        events=hp.read_jsonl(trio["EVENTS"])
        manifest=json.loads(trio["MANIFEST"].read_text())
        assert len(packets)==count==manifest["candidate_count"]
        assert sum(e["kind"]=="candidate_location" for e in events)==count
        enter=Counter(e["environment"] for e in events
                      if e["kind"]=="enter_local_environment")
        leave=Counter(e["environment"] for e in events
                      if e["kind"]=="exit_local_environment")
        assert enter==leave,(suffix,enter,leave)
        for row in packets:
            assert row["candidate_id"] not in all_ids
            all_ids.add(row["candidate_id"])
            assert row["section_start_line"]==start
        events_count.update(e["kind"] for e in events)
        inventory.append({
            "section_index":index,"key":suffix,
            "section_title":sec["section_title"],
            "section_label":sec["section_label"],
            "source_file":FILE,
            "source_start_line":start,"source_end_line":sec["section_end_line"],
            "source_lines":sec["section_end_line"]-start+1,
            "active_candidate_count":count,
            "actual_source_lemma_environments":enter["lemma"],
            "source_named_definition_environments":enter["definition"],
            "source_named_situation_environments":enter["situation"],
            "potential_persistent_context_lines":manifest["scope_review_leads"],
            "source_ref_count":manifest["unique_explicit_refs"],
            "source_ref_reuse_count":manifest["number_of_candidate_ref_reuses"],
            "packets":str(trio["PACKETS"]),
            "events":str(trio["EVENTS"]),
            "manifest":str(trio["MANIFEST"]),
            "status":"source_traversed_context_draft_not_yet_done",
            "all_lemma_local_assumptions_popped_after_environment":True,
        })
        prior_end=sec["section_end_line"]
    assert len(all_ids)==TOTAL
    out={
        "schema":"maththm.scoped-consecutive-sections-150.v1",
        "source_revision":REV,
        "chapter":FILE,
        "first_line":START,
        "last_line":END,
        "source_lines":END-START+1,
        "sections":SECTIONS,
        "consecutive_full_sections":True,
        "sections_with_zero_active_candidates":1,
        "active_candidate_count":len(all_ids),
        "source_events_by_kind":dict(sorted(events_count.items())),
        "section_inventory":inventory,
        "all_ids_distinct":True,
        "no_source_theorem_proof_read":True,
        "no_pass1_pass2_modification":True,
        "context_scope_automatically_inferred":False,
        "candidate_hypotheses_drafts_completed":0,
        "stage":"source_packets_ready_for_mathematical_context_review",
    }
    hp.atomic_text(ROOT/"MANIFEST.json",json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"chapter":FILE,"candidate_count":len(all_ids),
        "sections":len(inventory),"lines":END-START+1,
        "section_counts":[x["active_candidate_count"] for x in inventory],
        "context_signals":[(x["key"],x["potential_persistent_context_lines"])
                          for x in inventory if x["potential_persistent_context_lines"]]},
        ensure_ascii=False))
if __name__=="__main__":main()

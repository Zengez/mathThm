#!/usr/bin/env python3
"""Batch entire Stacks sections for source-order standalone candidate review.

Preset #1: five complete sections in Morphisms, 74 active candidate IDs.
No section is cut to hit a numerical target. Proofs ignored.
"""
import json
from pathlib import Path
from scripts import stacks_section_walk_pilot as sw
from scripts import harvest_pipeline as p
from scripts.stacks_context_recon import REV

SECTIONS=[
    ("morphisms.tex",1710,13,"affine"),
    ("morphisms.tex",3522,17,"quasi_finite"),
    ("morphisms.tex",5718,14,"syntomic"),
    ("morphisms.tex",6337,15,"differentials"),
    ("morphisms.tex",7603,15,"unramified"),
]
ROOT=Path("harvest/section_walk_scale74_2026-10-28")
def main():
    grouped,sections,unmatched=sw.groups()
    assert not unmatched
    total=0
    rows=[]
    ids=set()
    for filename,line,expected,key in SECTIONS:
        sec=next(x for x in sections[filename] if x["section_start_line"]==line)
        assert sec["chapter_title"] and sec["section_label"]
        assert len(grouped[(filename,line)])==expected
        out_prefix="SECTION_WALK_SCALE74_"+key.upper()
        # The core walker outputs 3 files into harvest; move them into
        # this isolated batch folder with a manifest and then continue.
        sw.pack(filename,line,Path("upstream/stacks"),
                limit=24,output_prefix=out_prefix)
        srcbase=Path("harvest")
        ROOT.mkdir(parents=True,exist_ok=True)
        data={}
        for suffix,ext in (("PACKETS","jsonl"),("EVENTS","jsonl"),("MANIFEST","json")):
            fromfile=srcbase/(out_prefix+"_"+suffix+"_2026-10-28."+ext)
            tofile=ROOT/(key+"_"+suffix.lower()+"."+ext)
            tofile.write_bytes(fromfile.read_bytes())
            fromfile.unlink()
            data[suffix]=tofile
        metadata=json.loads(data["MANIFEST"].read_text())
        assert metadata["candidate_count"]==expected
        packets=p.read_jsonl(data["PACKETS"])
        assert len(packets)==expected
        for q in packets:
            assert q["candidate_id"] not in ids
            assert q["section_start_line"]==line
            ids.add(q["candidate_id"])
        total+=expected
        rows.append({
            "source_file":filename,
            "section_start":line,
            "section_end":sec["section_end_line"],
            "section_title":sec["section_title"],
            "section_label":sec["section_label"],
            "candidate_count":expected,
            "packets_path":str(data["PACKETS"]),
            "events_path":str(data["EVENTS"]),
            "manifest_path":str(data["MANIFEST"]),
            "event_counts":metadata["event_counts"],
            "scope_lead_lines":metadata["scope_review_leads"],
            "named_reference_environments_seen":metadata["named_reference_environments_seen"],
        })
    assert total==74 and len(ids)==74
    manifest={
      "schema":"maththm.section-walk-scale-pilot.v1",
      "source_revision":REV,
      "section_count":len(rows),
      "selected_by_complete_section":True,
      "selected_chapter":"morphisms.tex",
      "target_approximate_candidates":75,
      "actual_candidate_count":total,
      "source_section_ranges_do_not_overlap":True,
      "sections":rows,
      "original_candidate_ids_unchanged":True,
      "theorem_proofs_read":False,
      "scope_assumptions_auto_imported":False,
      "standalone_drafts_not_yet_done":True
    }
    p.atomic_text(ROOT/"MANIFEST.json",json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,sort_keys=True))

if __name__=="__main__":main()

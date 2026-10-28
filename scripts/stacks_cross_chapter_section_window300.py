#!/usr/bin/env python3
"""Select 270..330 active candidates in a contiguous sequence spanning two
adjacent maintained Stacks chapters, with complete sections only.

Why cross chapter? No remaining chapter-local uninterrupted run reaches 270.
Never skip any section (including zero-candidate sections) and never cross an
already-drafted section. Source chapter conventions reset at boundaries.
"""
from __future__ import annotations
import json
from pathlib import Path
from scripts import harvest_pipeline as hp
from scripts import stacks_section_walk_pilot as sp
from scripts.stacks_consecutive_section_window150 import completed_section_starts

ROOT=Path("harvest/section_walk_scale300_2026-10-28")
LO,HI,TARGET=270,330,300
def main():
    grouped,byfile,unmatched=sp.groups()
    assert not unmatched
    excluded=completed_section_starts()
    chapter_list=sorted(
       [(v[0]["chapter_number"],filename,v) for filename,v in byfile.items() if v],
       key=lambda z:z[0])
    assert len({q[0] for q in chapter_list})==len(chapter_list),"chapter order must be unambiguous"
    windows=[]
    for (number_a,fa,sa),(number_b,fb,sb) in zip(chapter_list,chapter_list[1:]):
        # Do not skip chapters in the canonical maintained source ordering.
        assert number_b>number_a
        # Only suffix of A since we must continue through final A section.
        suffix=[]
        for section in reversed(sa):
            if section["section_start_line"] in excluded.get(fa,set()):break
            suffix.append(section)
        suffix.reverse()
        # Only prefix of B since we must start from its first section.
        prefix=[]
        for section in sb:
            if section["section_start_line"] in excluded.get(fb,set()):break
            prefix.append(section)
        if not suffix or not prefix:continue
        sa_counts=[len(grouped[(fa,s["section_start_line"])]) for s in suffix]
        sb_counts=[len(grouped[(fb,s["section_start_line"])]) for s in prefix]
        left=0
        for i in range(len(suffix)-1,-1,-1):
            left+=sa_counts[i]
            right=0
            for j in range(len(prefix)):
                right+=sb_counts[j]
                total=left+right
                if total>HI:break
                if total<LO:continue
                sections=([{"filename":fa,**dict(q),"active_candidate_count":sa_counts[z]}
                           for z,q in enumerate(suffix) if z>=i]+
                          [{"filename":fb,**dict(q),"active_candidate_count":sb_counts[z]}
                           for z,q in enumerate(prefix) if z<=j])
                assert len(sections)==len(suffix[i:])+len(prefix[:j+1])
                assert all(x["section_end_line"]+1==y["section_start_line"]
                           for x,y in zip(suffix[i:],suffix[i+1:]))
                assert all(x["section_end_line"]+1==y["section_start_line"]
                           for x,y in zip(prefix[:j+1],prefix[1:j+1]))
                all_lines=sum(x["section_end_line"]-x["section_start_line"]+1 for x in sections)
                refs=sum(len(raw.get("detected_local_references",[])) for x in sections
                         for _,raw,_ in grouped[(x["filename"],x["section_start_line"])])
                value={
                    "schema":"maththm.cross-chapter-contiguous-source-window.v1",
                    "source_revision":"a04446e57ec1fbc252a871afcec7752fb2807b14",
                    "chapter_pair":[fa,fb],
                    "chapter_order":[number_a,number_b],
                    "active_candidate_count":total,
                    "section_count":len(sections),
                    "source_lines":all_lines,
                    "source_reference_count":refs,
                    "empty_sections":sum(x["active_candidate_count"]==0 for x in sections),
                    "first_chapter_section_start":sections[0]["section_start_line"],
                    "last_chapter_section_end":sections[-1]["section_end_line"],
                    "source_chapter_boundary_is_contiguous":True,
                    "chapter_context_reset_required":True,
                    "sections":[{
                        "source_file":x["filename"],"start":x["section_start_line"],
                        "end":x["section_end_line"],"title":x["section_title"],
                        "label":x["section_label"],"candidate_count":x["active_candidate_count"],
                        "chapter_order":x["chapter_number"]
                    } for x in sections],
                }
                # Avoid massive segments and extremely high per-candidate
                # complexity. First preference fewer source lines/section.
                value["selection_score"]=round(
                    (all_lines/total)+len(sections)*0.8+
                    abs(total-TARGET)*0.1+refs*0.15,2)
                windows.append(value)
    windows.sort(key=lambda w:(w["selection_score"],w["source_lines"],
                                w["section_count"],w["chapter_order"][0]))
    ROOT.mkdir(parents=True,exist_ok=True)
    report={
       "schema":"maththm.cross-chapter-consecutive-section-selection.v1",
       "target":[LO,TARGET,HI],
       "valid_windows":len(windows),
       "adjacent_book_chapters_only":True,
       "excludes_completed_section_registry":True,
       "top_windows":windows[:30],
       "published_corpus_untouched":True,
    }
    hp.atomic_text(ROOT/"CROSS_CHAPTER_SELECTION.json",
                   json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    for x in windows[:12]:
        print(x["chapter_pair"],x["active_candidate_count"],
              x["section_count"],x["source_lines"],x["selection_score"])
    print("VALID_WINDOWS",len(windows))
if __name__=="__main__":main()

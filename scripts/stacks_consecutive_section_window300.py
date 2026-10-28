#!/usr/bin/env python3
"""Identify 270-330 candidate runs of consecutive full sections, excluding completed work."""
from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
from scripts import harvest_pipeline as hp
from scripts import stacks_section_walk_pilot as sp

OUT=Path("harvest/section_walk_scale300_2026-10-28")
USED={
    "morphisms.tex":{1710,3522,4615,5718,6337,7603},
    "limits.tex":{1729},
}
REGISTRY=Path("harvest/SECTION_WALK_COMPLETED_SECTIONS.json")
def completed_section_starts():
    result={key:set(value) for key,value in USED.items()}
    if REGISTRY.exists():
        entries=json.loads(REGISTRY.read_text(encoding="utf-8"))
        for entry in entries["sections"]:
            if entries["source_revision"]!=entry.get("source_revision",entries["source_revision"]):
                raise ValueError("Completed registry source revision mismatch")
            result.setdefault(entry["source_file"],set()).add(entry["section_start_line"])
    return result

def main():
    g,chapters,unmatched=sp.groups()
    assert not unmatched
    exclusions=completed_section_starts()
    windows=[]
    for filename,sections in chapters.items():
        if len(sections)<8:continue
        counts=[len(g.get((filename,s["section_start_line"]),[])) for s in sections]
        for lo in range(len(sections)):
            total=0
            for hi in range(lo,len(sections)):
                s=sections[hi]
                n=counts[hi]
                if s["section_start_line"] in exclusions.get(filename,set()):
                    break
                total+=n
                if total>330:break
                if total<270:continue
                size=sections[hi]["section_end_line"]-sections[lo]["section_start_line"]+1
                distinct=sum(counts[lo:hi+1])
                if distinct !=total:raise AssertionError("window bad")
                span=sections[lo:hi+1]
                empty=sum(counts[lo:hi+1].count(0) for _ in [0])
                refs=sum(len(raw.get("detected_local_references",[]))
                         for s0 in span
                         for _,raw,_ in g.get((filename,s0["section_start_line"]),[]))
                windows.append({
                    "source_file":filename,
                    "chapter_number":sections[lo]["chapter_number"],
                    "section_count":len(span),
                    "candidate_count":total,
                    "source_lines":size,
                    "source_refs":refs,
                    "empty_sections":empty,
                    "first_line":span[0]["section_start_line"],
                    "last_line":span[-1]["section_end_line"],
                    "titles":[s0["section_title"] for s0 in span],
                    "sections":[{"first":s0["section_start_line"],"last":s0["section_end_line"],
                                 "label":s0["section_label"],"title":s0["section_title"],
                                 "count":counts[lo+j]} for j,s0 in enumerate(span)],
                    "source_revision":"a04446e57ec1fbc252a871afcec7752fb2807b14",
                })
    # Prefer compact runs and fewer sections to lower context overhead; keep
    # all candidate windows for independent choice, no artificial cutpoints.
    windows.sort(key=lambda w:(w["source_lines"]/w["candidate_count"]+
                                w["section_count"]*8+
                                w["source_refs"]*.25+
                                abs(w["candidate_count"]-300)*0.65,
                                w["source_lines"],
                                w["source_file"],w["first_line"]))
    report={
        "schema":"maththm.consecutive-full-section-window-options.v1",
        "total_valid_windows":len(windows),
        "target_band":[270,330],
        "excluded_prior_section_starts":{k:sorted(v) for k,v in exclusions.items()},
        "top_35":windows[:35],
        "all_windows_statistics":{
            "chapters_with_windows":len({w["source_file"] for w in windows}),
            "smallest_source_lines":min((x["source_lines"] for x in windows),default=None),
        },
        "nothing_processed_or_published":True,
    }
    OUT.mkdir(parents=True,exist_ok=True)
    hp.atomic_text(OUT/"SELECTION_OPTIONS.json",json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    for i,w in enumerate(windows[:15],1):
        print(i,w["source_file"],w["first_line"],w["last_line"],
              w["candidate_count"],w["section_count"],w["source_lines"],
              " :: ",", ".join(w["titles"][:6]))
    print("TOTAL_WINDOWS",len(windows))
if __name__=="__main__":main()

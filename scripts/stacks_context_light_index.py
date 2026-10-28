#!/usr/bin/env python3
"""Pinned Stacks section opening and exact label locators. Mechanical only."""
from __future__ import annotations

import argparse
import bisect
import json
import re
from functools import lru_cache
from pathlib import Path

from scripts import harvest_pipeline as p
from scripts.stacks_context_recon import REV, URL, ordered_chapters, book_parts
from scripts.stacks_context_index import get_candidate_context_leads

BASE = Path("harvest")
OPENINGS = BASE / "stacks_context_openings_2026-10-28.jsonl"
LABELS = BASE / "stacks_context_labels_2026-10-28.json"
MANIFEST = BASE / "stacks_context_light_index_manifest_2026-10-28.json"
REPORT = BASE / "stacks_context_light_index_summary_2026-10-28.md"

SECTION = re.compile(r"\\section(?:\[[^\]\n]*\])?\{([^}\n]+)\}")
SUBSECTION = re.compile(r"\\subsection(?:\[[^\]\n]*\])?\{([^}\n]+)\}")
TITLE = re.compile(r"\\title\{([^}\n]+)\}")
LABEL = re.compile(r"\\label\{([^}\n]+)\}")
BEGIN = re.compile(r"\\begin\{([a-zA-Z*]+)\}")
END = re.compile(r"\\end\{([a-zA-Z*]+)\}")
FORMAL = {"lemma","theorem","proposition","corollary","definition","remark",
          "remarks","example","exercise","situation","construction","setup",
          "notation","proof"}
KIND = FORMAL | {"equation","item","section","subsection","subsubsection"}
CONTEXT = re.compile(r"(?i)\b(?:assum|throughout|convention|notation|fix|"
                     r"we will|we work|let us|suppose|in this section|"
                     r"in this chapter|base scheme|site|topolog|denote)\b")

def uncomment(line):
    for i, c in enumerate(line):
        if c == "%" and (i == 0 or line[i-1] != "\\"):
            return line[:i]
    return line

def scan_file(text, filename, chapter_number, book_part):
    lines = [uncomment(s) for s in text.splitlines()]
    stem = Path(filename).stem
    mt = TITLE.search("\n".join(lines[:45]))
    title = mt.group(1) if mt else stem
    sections = []
    subsections = []
    for n, line in enumerate(lines, 1):
        m = SECTION.search(line)
        if m:
            sections.append({"line":n,"title":m.group(1),"label":None})
        m = SUBSECTION.search(line)
        if m:
            subsections.append({"line":n,"title":m.group(1),"label":None})
    for items in (sections, subsections):
        for section in items:
            for i in range(section["line"]+1, min(section["line"]+4,len(lines)+1)):
                m = LABEL.search(lines[i-1])
                if m:
                    section["label"] = m.group(1)
                    break
    starts = [s["line"] for s in sections]
    substarts = [s["line"] for s in subsections]
    openings = []
    for j, section in enumerate(sections):
        start = section["line"]
        end = sections[j+1]["line"] if j+1 < len(sections) else len(lines)+1
        nxt = bisect.bisect_right(substarts,start)
        if nxt < len(substarts):
            end = min(end,substarts[nxt])
        formal_end = end
        for line_no in range(start+1,end):
            if any(m.group(1).lower().rstrip("*") in FORMAL for m in BEGIN.finditer(lines[line_no-1])):
                formal_end = line_no
                break
        prose = []
        count = 0
        end_included = start
        for line_no in range(start+1,formal_end):
            line = lines[line_no-1].strip()
            if not line or LABEL.fullmatch(line) or line in (r"\noindent",r"\medskip\noindent"):
                continue
            prose.append((line_no,line))
        preview = []
        preview_length = 0
        for line_no,line in prose:
            if len(preview)>=55 or preview_length+len(line)>1800:
                break
            preview.append(line)
            preview_length += len(line)+1
            end_included = line_no
        snippet = "\n".join(preview)
        openings.append({
            "filename":filename,"chapter_number":chapter_number,
            "chapter_title":title,"book_part":book_part,
            "section_title":section["title"],"section_label":section["label"],
            "section_start_line":start,
            "section_end_line":sections[j+1]["line"]-1 if j+1<len(sections) else len(lines),
            "opening_start_line":start+1,"opening_end_line":formal_end-1,
            "preview_last_line":end_included,
            "opening_preview":snippet,
            "opening_total_chars":sum(len(line)+1 for _,line in prose),
            "preview_truncated":len(preview)<len(prose),
            "source_url":URL+filename+"#L"+str(start),
            "opening_context_hint":bool(CONTEXT.search(snippet)),
            "is_chapter_introduction":section["title"].strip().lower()=="introduction",
            "source_revision":REV,
            "uninterpreted_source_lead":True,
        })
    labels = []
    in_proof = False
    last_env = ""
    for i,line in enumerate(lines,1):
        for m in BEGIN.finditer(line):
            if m.group(1).lower()=="proof":
                in_proof=True
            else:
                last_env=m.group(1).lower()
        if in_proof:
            if re.search(r"\\end\{proof\}",line):
                in_proof=False
            continue
        if END.search(line):
            last_env=""
        sec_index=bisect.bisect_right(starts,i)-1
        sub_index=bisect.bisect_right(substarts,i)-1
        section=sections[sec_index] if sec_index>=0 else None
        subsection=(subsections[sub_index] if sub_index>=0
                    and (section is None or subsections[sub_index]["line"]>section["line"])
                    else None)
        for m in LABEL.finditer(line):
            raw=m.group(1)
            typ=raw.split("-",1)[0]
            if typ not in KIND:
                typ=last_env if last_env in KIND else "other"
            labels.append({
                "full":stem+"-"+raw,"local":raw,
                "value":[filename,i,typ,section["label"] if section else None,
                         subsection["label"] if subsection else None],
            })
    return {"sections":len(sections),"subsections":len(subsections),
            "lines":len(lines),"title":title,"openings":openings,"labels":labels}

def build(root:Path, out:Path=BASE):
    chapters=ordered_chapters(root)
    assert len(chapters)==115
    parts=book_parts(root)
    openings=[]
    full={}
    locals_by_chapter={}
    per_chapter={}
    for index,stem in enumerate(chapters,1):
        src=root/(stem+".tex")
        if not src.is_file():
            raise FileNotFoundError(src)
        data=scan_file(src.read_text(encoding="utf-8"),src.name,index,parts.get(stem))
        openings.extend(data["openings"])
        per_chapter[stem]={"lines":data["lines"],"title":data["title"],
                            "sections":data["sections"],"subsections":data["subsections"],
                            "labels":len(data["labels"])}
        local={}
        for row in data["labels"]:
            full.setdefault(row["full"],[]).append(row["value"])
            local.setdefault(row["local"],[]).append(row["value"])
        locals_by_chapter[stem]=local
    labeldata={
        "schema":"maththm.stacks-exact-label-lookup.v1",
        "source_revision":REV,
        "values_schema":["filename","line","kind","section_label","subsection_label"],
        "by_full_label":full,
        "by_local_chapter_label":locals_by_chapter,
        "full_label_collisions":[x for x,v in full.items() if len(v)>1],
        "proof_body_labels_excluded":True,"no_context_research":True
    }
    manifest={
        "schema":"maththm.stacks-light-context-index.v1",
        "source_revision":REV,"chapters_scanned":len(chapters),
        "section_openings":len(openings),
        "subsections_located":sum(x["subsections"] for x in per_chapter.values()),
        "source_labels_indexed":sum(x["labels"] for x in per_chapter.values()),
        "unique_full_label_keys":len(full),
        "duplicate_full_labels":len(labeldata["full_label_collisions"]),
        "opening_previews_nonempty":sum(bool(x["opening_preview"]) for x in openings),
        "opening_previews_truncated":sum(x["preview_truncated"] for x in openings),
        "opening_previews_with_context_clues":sum(x["opening_context_hint"] for x in openings),
        "chapter_introduction_sections":sum(x["is_chapter_introduction"] for x in openings),
        "preview_limit_chars":1800,
        "preview_limit_nonblank_lines":55,
        "per_chapter":per_chapter,
        "files":{"openings":str(OPENINGS),"labels":str(LABELS)},
        "candidate_statements_modified":False,"hypotheses_inferred":False,
        "theorem_proofs_read":False,"recursive_context_research":False,
    }
    out.mkdir(parents=True,exist_ok=True)
    p.atomic_text(OPENINGS,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in openings))
    p.atomic_text(LABELS,json.dumps(labeldata,ensure_ascii=False,separators=(",",":"),sort_keys=True)+"\n")
    p.atomic_text(MANIFEST,json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    report=[
        "# Stacks mechanical section openings and labels",
        "",
        "Pinned source: "+REV+". All results are unreviewed leads, not theorem hypotheses.",
        "",
        f"- Chapters: {len(chapters)}",
        f"- Section openings: {len(openings)}",
        f"- Distinct exact source labels: {len(full)}",
        f"- Label collisions: {manifest['duplicate_full_labels']}",
        f"- Opening previews truncated to 1800 characters / 55 substantive lines: {manifest['opening_previews_truncated']}",
        "",
        "## Files",
        "",
        "- [Opening previews](stacks_context_openings_2026-10-28.jsonl)",
        "- [Exact label index](stacks_context_labels_2026-10-28.json)",
        "- [Index manifest](stacks_context_light_index_manifest_2026-10-28.json)",
        "- [Reviewed designated conventions atlas](stacks_standing_context_atlas_2026-10-28.jsonl)",
        "",
        "No proof content, transitive references, or mathematical claims have been processed.",
    ]
    p.atomic_text(REPORT,"\n".join(report)+"\n")
    print(json.dumps({k:manifest[k] for k in ("chapters_scanned","section_openings",
        "source_labels_indexed","unique_full_label_keys","duplicate_full_labels",
        "opening_previews_nonempty","opening_previews_truncated")},sort_keys=True))
    return manifest

@lru_cache(maxsize=1)
def label_index():
    return json.loads(LABELS.read_text(encoding="utf-8"))

@lru_cache(maxsize=1)
def openings_by_chapter():
    grouped={}
    for line in p.read_jsonl(OPENINGS):
        grouped.setdefault(Path(line["filename"]).stem,[]).append(line)
    for rows in grouped.values():
        rows.sort(key=lambda r:r["section_start_line"])
    return grouped

def exact_label(chapter,reference):
    data=label_index()
    local=data["by_local_chapter_label"].get(chapter,{}).get(reference,[])
    if local:
        matches=local
        mode="local"
    else:
        matches=data["by_full_label"].get(reference,[])
        mode="full_cross_chapter"
    return {
        "reference":reference,
        "status":"resolved_exact" if len(matches)==1 else "ambiguous" if matches else "unresolved",
        "matching_mode":mode if matches else None,
        "matches":[{
            "filename":x[0],"line":x[1],"kind":x[2],
            "section_label":x[3],"subsection_label":x[4],
            "source_url":URL+x[0]+"#L"+str(x[1])
        } for x in matches],
    }

def candidate_context_bundle(filename,statement_line,refs=(),*,max_refs=8):
    if not isinstance(statement_line,int) or statement_line<1:
        raise ValueError("statement_line must be positive")
    chapter=Path(filename).stem
    items=openings_by_chapter().get(chapter)
    if not items:
        return {"status":"source_chapter_not_indexed","chapter":chapter}
    starts=[x["section_start_line"] for x in items]
    k=bisect.bisect_right(starts,statement_line)-1
    section=items[k] if k>=0 else None
    intro=next((x for x in items if x["is_chapter_introduction"]),None)
    resolved=[]
    seen=set()
    for ref in refs:
        if ref not in seen and len(resolved)<max_refs:
            resolved.append(exact_label(chapter,ref))
            seen.add(ref)
    conv=get_candidate_context_leads(filename,statement_line=statement_line)
    return {
        "chapter":chapter,"statement_line":statement_line,
        "status":"lookup_leads_only",
        "source_revision":REV,
        "current_section_opening":section,
        "chapter_introduction_opening":intro,
        "explicit_label_references":resolved,
        "additional_ref_count_not_looked_up":max(0,len(set(refs))-len(resolved)),
        "standing_convention_leads":conv["context_leads"],
        "candidate_specific_scope_review_required":True,
        "proofs_unread":True,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-root",default="upstream/stacks")
    opts=parser.parse_args()
    build(Path(opts.source_root))

if __name__=="__main__":
    main()

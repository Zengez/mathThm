#!/usr/bin/env python3
"""Bounded chapter/section candidate grouping and scope-event pilot.

This is a source-ordered work-queue builder, not a parser that claims to
interpret standing assumptions or theorem truth. Proofs are never inspected.
Context state distinguishes scoped local theorem/definition statements from
explicitly durable section/chapter declarations; no automatic propagation.
"""
from __future__ import annotations
import argparse, bisect, json, re
from collections import Counter, defaultdict
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.active_candidate_pool import IDS, BATCHES
from scripts.stacks_context_light_index import OPENINGS, candidate_context_bundle, exact_label
from scripts.stacks_context_recon import REV, URL

OUT=Path("harvest")
RANK=OUT/"SECTION_WALK_PILOT_RANK_2026-10-28.json"
PACKETS=OUT/"SECTION_WALK_PILOT_PACKETS_2026-10-28.jsonl"
SUMMARY=OUT/"SECTION_WALK_PILOT_MANIFEST_2026-10-28.json"
EVENTS=OUT/"SECTION_WALK_PILOT_EVENTS_2026-10-28.jsonl"
FRAME_BEGIN=re.compile(r"\\begin\{(lemma|proposition|theorem|corollary|situation|notation|setup|definition|remark|construction|example)\}")
FRAME_END=re.compile(r"\\end\{(lemma|proposition|theorem|corollary|situation|notation|setup|definition|remark|construction|example)\}")
PROOF_BEGIN=re.compile(r"\\begin\{proof\}")
PROOF_END=re.compile(r"\\end\{proof\}")
LABEL=re.compile(r"\\label\{([^}]+)\}")
NAMED_REF=re.compile(r"\\ref\{([^}]+)\}")
BROAD_SCOPE=re.compile(r"(?i)\b(?:throughout (?:this|the|whole) (?:section|chapter)"
 r"|for the (?:rest|remainder) of (?:this|the) (?:section|chapter)"
 r"|in this (?:section|chapter) we (?:assume|fix|work)"
 r"|in what follows we (?:assume|fix|work)"
 r"|unless otherwise (?:specified|stated)|from now on"
 r"|we (?:will|shall) work in the following situation)\b")
MAYBE_SCOPE=re.compile(r"(?i)\b(?:we (?:assume|fix|work with|shall assume)|"
 r"let (?:us|the following)|suppose|we use the notation|as above)\b")
FORMAL_SET={"lemma","proposition","theorem","corollary"}
REFERENCE_SET={"situation","notation","setup","definition","construction","remark"}

def selected_candidates():
    active=p.load_rows(IDS,"candidate_id")
    assert len(active)==9675,len(active)
    pass1={}
    pass2={}
    for batch in BATCHES:
        d=Path("harvest/batches")/batch
        for row in p.read_jsonl(d/"pass1.jsonl"):
            if row["candidate_id"] in active:
                pass1[row["candidate_id"]]=row
        for row in p.read_jsonl(d/"pass2.jsonl"):
            if row["candidate_id"] in active:
                pass2[row["candidate_id"]]=row
    assert set(pass1)==set(pass2)==set(active)
    # Canonical merged input may retain both source occurrence IDs, so do not
    # index aliases as independently active until later merge adjudication.
    return pass1,pass2

def section_index():
    byfile=defaultdict(list)
    for r in p.read_jsonl(OPENINGS):
        byfile[r["filename"]].append(r)
    for entries in byfile.values():
        entries.sort(key=lambda r:r["section_start_line"])
    return byfile

def groups():
    pass1,pass2=selected_candidates()
    sections=section_index()
    grouped=defaultdict(list)
    unmatched=[]
    for ident,raw in pass1.items():
        src=raw["source"]
        file=src["filename"]
        line=src["statement_line"]
        choices=sections.get(file,[])
        starts=[s["section_start_line"] for s in choices]
        idx=bisect.bisect_right(starts,line)-1
        if idx<0:
            unmatched.append(ident)
            continue
        sec=choices[idx]
        if line>sec["section_end_line"]:
            raise AssertionError((file,line,sec))
        group=(file,sec["section_start_line"])
        grouped[group].append((ident,raw,pass2[ident]))
    return grouped,sections,unmatched

def rank():
    grouped,sections,unmatched=groups()
    rows=[]
    for (filename,first),cands in grouped.items():
        sec=next(s for s in sections[filename] if s["section_start_line"]==first)
        count=len(cands)
        length=sec["section_end_line"]-first+1
        refs=sum(len(raw.get("detected_local_references",[])) for _,raw,_ in cands)
        score=(
            min(count,18)*5 + (18 if 7<=count<=20 else 0)
            + (7 if length<=450 else 0)
            + (5 if refs>=3 else 0)
            - max(0,count-24)*6
            - max(0,length-650)//30
        )
        rows.append({
            "file":filename,"section_start_line":first,
            "section_label":sec["section_label"],
            "section_title":sec["section_title"],
            "section_end_line":sec["section_end_line"],
            "section_lines":length,
            "candidate_count":count,
            "candidate_lines":sorted(raw["source"]["statement_line"] for _,raw,_ in cands),
            "explicit_reference_count":refs,
            "score":score,
            "chapter_order":sec["chapter_number"],
            "section_opening_preview":sec["opening_preview"][:450],
        })
    rows.sort(key=lambda x:(-x["score"],x["chapter_order"],x["section_start_line"]))
    counts=Counter(len(x) for x in grouped.values())
    report={
        "schema":"maththm.section-walk-rank.v1",
        "source_revision":REV,
        "active_canonical_candidate_ids":9675,
        "candidates_with_indexed_section":sum(len(c) for c in grouped.values()),
        "candidates_before_first_section":len(unmatched),
        "populated_sections":len(rows),
        "sections_with_at_least_8_candidates":sum(r["candidate_count"]>=8 for r in rows),
        "section_candidate_sizes":dict(sorted((str(k),v) for k,v in counts.items())),
        "ranked_sections":rows[:35],
        "data_only_not_semantically_interpreted":True,
    }
    p.atomic_text(RANK,json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({k:report[k] for k in ("active_canonical_candidate_ids",
        "candidates_with_indexed_section","candidates_before_first_section",
        "populated_sections","sections_with_at_least_8_candidates")},sort_keys=True))
    print("TOP:",[(r["file"],r["section_title"],r["candidate_count"],
                    r["section_lines"],r["section_start_line"]) for r in rows[:12]])
    return report

def without_comments(s):
    # Only remove true TeX comments, preserving \% as a literal symbol.
    return re.split(r"(?<!\\)%",s,maxsplit=1)[0]

def walk_events(lines, section, candlines):
    """Physical scope stack; reference environments are NOT ambient premises.

    No scoped hypotheses leave their enclosing environment. Unclassified
    outer prose is a review lead, not an assumed persistent declaration.
    """
    first=section["section_start_line"]
    last=section["section_end_line"]
    events=[]
    frames=[]
    scope_candidates=[]
    available_named=[]
    inproof=False
    para=[]
    def flush_para():
        nonlocal para
        if not para:
            return
        content=" ".join(s for _,s in para)
        start=para[0][0]
        if BROAD_SCOPE.search(content):
            signal="potential_durable_scope_change"
        elif MAYBE_SCOPE.search(content):
            signal="local_or_unclassified_prose"
        else:
            para=[]
            return
        frame=[x["kind"] for x in frames]
        # Do not claim 'throughout' persistence without a scope review.
        events.append({"line":start,"kind":signal,"scope_stack":frame,
                       "text_excerpt":content[:850],"review_required":True})
        scope_candidates.append(start)
        para=[]
    for lineno in range(first,last+1):
        line=without_comments(lines[lineno-1]).strip()
        if PROOF_BEGIN.search(line):
            flush_para()
            inproof=True
            events.append({"line":lineno,"kind":"proof_skipped",
                           "scope_stack":[x["kind"] for x in frames]})
        if inproof:
            if PROOF_END.search(line):
                inproof=False
            continue
        starts=list(FRAME_BEGIN.finditer(line))
        ends=list(FRAME_END.finditer(line))
        if starts or ends:
            flush_para()
        for begin in starts:
            kind=begin.group(1)
            frames.append({"kind":kind,"line":lineno})
            events.append({"line":lineno,"kind":"enter_local_environment",
                           "environment":kind,
                           "scope_stack":[x["kind"] for x in frames],
                           "persists_after_end":False})
            if kind in REFERENCE_SET:
                for probe in lines[lineno:min(lineno+3,last)]:
                    lm=LABEL.search(probe)
                    if lm:
                        available_named.append({"kind":kind,"label":lm.group(1),
                            "line":lineno})
                        break
        for end in ends:
            kind=end.group(1)
            if not frames or frames[-1]["kind"]!=kind:
                raise ValueError(f"Unexpected environment end {kind} at {lineno} in {section['filename']}")
            events.append({"line":lineno,"kind":"exit_local_environment",
                           "environment":kind,
                           "scope_stack_before_pop":[x["kind"] for x in frames],
                           "persists_after_end":False})
            frames.pop()
        if not starts and not ends and not frames:
            if not line or line.startswith("\\section") or line.startswith("\\label") or line.startswith("\\noindent") or line.startswith("\\medskip"):
                flush_para()
            elif line.startswith("\\"):
                flush_para()
            else:
                para.append((lineno,line))
        if lineno in candlines:
            flush_para()
            events.append({"line":lineno,"kind":"candidate_location",
                           "scope_stack":[x["kind"] for x in frames]})
    flush_para()
    if frames or inproof:
        raise ValueError(f"Unbalanced source context at {section['filename']}:{last}: {frames} proof={inproof}")
    return events,scope_candidates,available_named

def pack(file,section_start,source_root,limit=24,output_prefix="SECTION_WALK_PILOT",
         group_data=None):
    grouped,sections,unmatched=group_data if group_data is not None else groups()
    key=(file,section_start)
    if file not in sections or not any(
            s["section_start_line"]==section_start for s in sections[file]):
        raise ValueError(f"Section not indexed: {key}")
    section=next(s for s in sections[file] if s["section_start_line"]==section_start)
    cands=sorted(grouped[key],key=lambda r:(r[1]["source"]["statement_line"],r[0]))
    if len(cands)>limit:
        raise ValueError(f"{len(cands)} candidates exceeds {limit}-item cap; choose another section")
    lines=(source_root/file).read_text(encoding="utf-8").splitlines()
    events,scope_candidates,available_named=walk_events(
        lines,section,set(x[1]["source"]["statement_line"] for x in cands))
    output=[]
    refs_seen=set()
    for i,(ident,raw,p2) in enumerate(cands):
        line=raw["source"]["statement_line"]
        opening=section["opening_preview"]
        refs=list(dict.fromkeys(raw.get("detected_local_references",[])))
        # Source text may contain labels not found by preliminary heuristic.
        refs.extend(m.group(1) for m in NAMED_REF.finditer(raw["statement_tex"])
                    if m.group(1) not in refs)
        refs=list(dict.fromkeys(refs))[:8]
        lookups=[exact_label(Path(file).stem,ref) for ref in refs]
        new_refs=[x for x in refs if x not in refs_seen]
        refs_seen.update(refs)
        prev=cands[i-1][1]["source"]["statement_line"] if i else section_start
        between=[e for e in events if prev<=e["line"]<=line
                 and e["kind"] in ("potential_durable_scope_change","local_or_unclassified_prose",
                                   "enter_local_environment","exit_local_environment")]
        output.append({
          "schema":"maththm.section-walk-candidate.v1",
          "candidate_id":ident,"source_revision":REV,
          "source_filename":file,"source_statement_line":line,
          "source_url":raw["source"]["source_url"] if "source_url" in raw["source"] else URL+file+"#L"+str(line),
          "source_label":raw["source"].get("label"),
          "section_title":section["section_title"],
          "section_label":section["section_label"],
          "section_start_line":section_start,
          "statement_tex":raw["statement_tex"][:6500],
          "statement_truncated":len(raw["statement_tex"])>6500,
          "prior_hypotheses":p2["hypotheses"][:10],
          "prior_conclusions":p2["conclusions"][:10],
          "prior_context_status":p2["context_status"],
          "explicit_refs":lookups,
          "new_refs_in_this_candidate":new_refs,
          "available_prior_named_context":[d for d in available_named if d["line"]<line][-12:],
          "context_events_since_previous_candidate":between[-18:],
          "section_opening_preview":opening if i==0 else None,
          "candidate_review_status":"needs_actual_mathematical_standalone_reconstruction",
          "ambient_context_auto_assumed":False,
          "provisional_durable_scope_assertions":[],
          "proof_screened":False,
        })
    manifest={
        "schema":"maththm.section-walk-pilot.v1","source_revision":REV,
        "section":{"file":file,"line_start":section_start,
                   "line_end":section["section_end_line"],
                   "title":section["section_title"],"label":section["section_label"]},
        "candidate_count":len(output),
        "source_lines_in_section":section["section_end_line"]-section_start+1,
        "event_counts":dict(Counter(e["kind"] for e in events)),
        "scope_review_leads":scope_candidates,
        "named_reference_environments_seen":len(available_named),
        "unique_explicit_refs":len(refs_seen),
        "number_of_candidate_ref_reuses":sum(
            len(q["explicit_refs"])-len(q["new_refs_in_this_candidate"]) for q in output),
        "proofs_read":False,"mathematical_statements_interpreted":False,
        "scope_changes_validated":False,
        "original_source_modified":False,
        "candidate_rewrites_completed":0,
        "note":"Physical scope stack pops at end of each local environment; durable prose signals require human adjudication before any persistent state is activated.",
    }
    if not re.fullmatch(r"[A-Z0-9_]+",output_prefix):
        raise ValueError("Unsafe output_prefix")
    p.atomic_text(OUT/(output_prefix+"_PACKETS_2026-10-28.jsonl"),"".join(
        json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in output))
    p.atomic_text(OUT/(output_prefix+"_EVENTS_2026-10-28.jsonl"),"".join(
        json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in events))
    p.atomic_text(OUT/(output_prefix+"_MANIFEST_2026-10-28.json"),
                  json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps(manifest,sort_keys=True))
    return manifest

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=["rank","pack"])
    parser.add_argument("--file")
    parser.add_argument("--line",type=int)
    parser.add_argument("--source-root",default="upstream/stacks")
    parser.add_argument("--output-prefix",default="SECTION_WALK_PILOT")
    args=parser.parse_args()
    if args.mode=="rank":rank()
    else:
        if not args.file or not args.line:
            parser.error("pack requires --file and --line")
        pack(args.file,args.line,Path(args.source_root),output_prefix=args.output_prefix)

if __name__=="__main__": main()

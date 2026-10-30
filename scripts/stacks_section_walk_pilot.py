#!/usr/bin/env python3
"""Proof-free section indexing, candidate grouping and chronological scope events.

Only the operations required by current Stage A preparation are retained.
Historical ranking/packing pilots remain available in Git history.
"""
from __future__ import annotations

import bisect
import re
from collections import defaultdict
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.active_candidate_pool import IDS, BATCHES
from scripts.stacks_context_light_index import OPENINGS

FRAME_BEGIN=re.compile(r"\\begin\{(lemma|proposition|theorem|corollary|situation|notation|setup|definition|remark|construction|example)\}")
FRAME_END=re.compile(r"\\end\{(lemma|proposition|theorem|corollary|situation|notation|setup|definition|remark|construction|example)\}")
PROOF_BEGIN=re.compile(r"\\begin\{proof\}")
PROOF_END=re.compile(r"\\end\{proof\}")
LABEL=re.compile(r"\\label\{([^}]+)\}")
BROAD_SCOPE=re.compile(r"(?i)\b(?:throughout (?:this|the|whole) (?:section|chapter)"
 r"|for the (?:rest|remainder) of (?:this|the) (?:section|chapter)"
 r"|in this (?:section|chapter) we (?:assume|fix|work)"
 r"|in what follows we (?:assume|fix|work)"
 r"|unless otherwise (?:specified|stated)|from now on"
 r"|we (?:will|shall) work in the following situation)\b")
MAYBE_SCOPE=re.compile(r"(?i)\b(?:we (?:assume|fix|work with|shall assume)|"
 r"let (?:us|the following)|suppose|we use the notation|as above)\b")
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
    # Construct section starts once per chapter, not once per candidate.
    starts_by_file = {name: [s["section_start_line"] for s in rows]
                      for name, rows in sections.items()}
    for ident,raw in pass1.items():
        src=raw["source"]
        file=src["filename"]
        line=src["statement_line"]
        choices=sections.get(file,[])
        idx=bisect.bisect_right(starts_by_file.get(file, ()),line)-1
        if idx<0:
            unmatched.append(ident)
            continue
        sec=choices[idx]
        if line>sec["section_end_line"]:
            raise AssertionError((file,line,sec))
        group=(file,sec["section_start_line"])
        grouped[group].append((ident,raw,pass2[ident]))
    return grouped,sections,unmatched


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


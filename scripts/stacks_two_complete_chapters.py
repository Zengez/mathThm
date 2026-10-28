#!/usr/bin/env python3
"""Two complete adjacent Stacks chapters, with source-grounded draft overlays.

No candidate quota or partial sections. Heuristic editorial drafts, never
final mathematical source-equivalence approvals or proof screening.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as hp
from scripts import stacks_section_walk_pilot as sp
from scripts import stacks_scale300_context_passages as contexts
from scripts import stacks_section_walk_scale300_reconstruct as r300
from scripts.stacks_section_walk_scale150_reconstruct import local_frames
from scripts.stacks_consecutive_section_window150 import completed_section_starts
from scripts.stacks_context_recon import REV

ROOT=Path("harvest/section_walk_two_chapters_2026-10-28")
REGISTRY=Path("harvest/SECTION_WALK_COMPLETED_SECTIONS.json")
PAIR=(32,33) # Immediately following the previously used chapter 31.
BATCH="two_full_chapters_2026-10-28"
READY=r300.READY
HOLD=r300.HOLD
KINDS={"definition","situation","notation","setup","construction"}

def write(path, value):
    hp.atomic_text(path,json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n")

def inventory():
    grouped,byfile,unmatched=sp.groups()
    assert not unmatched, ("unmatched active candidates",len(unmatched))
    chapters={}
    for filename,sections in byfile.items():
        assert len({s["chapter_number"] for s in sections})==1
        number=sections[0]["chapter_number"]
        assert number not in chapters,("duplicate chapter index",number)
        chapters[number]=(filename,sections)
    for n in PAIR:
        assert n in chapters,("missing chapter",n)
    used=completed_section_starts()
    choices=[]
    for n in PAIR:
        filename,sections=chapters[n]
        assert sections,filename
        for i,s in enumerate(sections):
            if i:
                assert sections[i-1]["section_end_line"]+1==s["section_start_line"],(filename,s)
            assert s["section_start_line"] not in used.get(filename,set()), ("already completed",filename,s["section_start_line"])
            choices.append({
                "source_filename":filename,"chapter_order":n,
                "section_start_line":s["section_start_line"],
                "section_end_line":s["section_end_line"],
                "section_title":s["section_title"],
                "section_label":s["section_label"],
                "active_candidate_count":len(grouped.get((filename,s["section_start_line"]),[])),
            })
    assert choices[0]["chapter_order"]==32 and choices[-1]["chapter_order"]==33
    assert all(choices[i]["chapter_order"]<=choices[i+1]["chapter_order"] for i in range(len(choices)-1))
    assert sum(s["active_candidate_count"] for s in choices)>0
    assert all(choices[0]["section_start_line"]==chapters[32][1][0]["section_start_line"] for _ in [0])
    assert choices[-1]["section_end_line"]==chapters[33][1][-1]["section_end_line"]
    return grouped,byfile,unmatched,choices,chapters

def stage():
    ROOT.mkdir(parents=True,exist_ok=True)
    grouped,byfile,unmatched,choices,chapters=inventory()
    selection={"schema":"maththm.two-complete-chapters.selection.v1",
               "source_revision":REV,"chapters":[{"order":n,"source_filename":chapters[n][0],
               "section_count":len(chapters[n][1])} for n in PAIR],
               "all_source_sections_included":True,
               "candidate_count":sum(x["active_candidate_count"] for x in choices),
               "section_count":len(choices),
               "source_lines":sum(s["section_end_line"]-s["section_start_line"]+1 for s in choices),
               "no_candidate_target_or_cutoff":True,
               "sections":choices}
    write(ROOT/"SELECTION.json",selection)
    inventory_rows=[]
    seen=set()
    event_counts=Counter()
    for i,s in enumerate(choices,1):
        filename=s["source_filename"]
        start=s["section_start_line"]
        key=f"s{i:03d}"
        prefix=f"TWOCH_{key.upper()}"
        count=s["active_candidate_count"]
        sp.pack(filename,start,Path("upstream/stacks"),limit=max(24,count),
                output_prefix=prefix,group_data=(grouped,byfile,unmatched))
        paths={}
        for typ,ext in (("PACKETS","jsonl"),("EVENTS","jsonl"),("MANIFEST","json")):
            orig=Path("harvest")/f"{prefix}_{typ}_2026-10-28.{ext}"
            dest=ROOT/f"{key}_{typ.lower()}.{ext}"
            dest.write_bytes(orig.read_bytes())
            orig.unlink()
            paths[typ]=dest
        packets=hp.read_jsonl(paths["PACKETS"])
        events=hp.read_jsonl(paths["EVENTS"])
        local_m=json.loads(paths["MANIFEST"].read_text())
        assert len(packets)==count==local_m["candidate_count"],key
        assert sum(e["kind"]=="candidate_location" for e in events)==count,key
        assert sum(e["kind"]=="enter_local_environment" for e in events)==sum(e["kind"]=="exit_local_environment" for e in events),key
        for p in packets:
            assert p["candidate_id"] not in seen,p["candidate_id"]
            seen.add(p["candidate_id"])
        event_counts.update(e["kind"] for e in events)
        inventory_rows.append({"section_index":i,"key":key,**s,
            "packets":str(paths["PACKETS"]),"events":str(paths["EVENTS"]),
            "source_lemma_environments":sum(e["kind"]=="enter_local_environment" and e["environment"]=="lemma" for e in events),
            "source_proof_environments_skipped":local_m["event_counts"].get("proof_skipped",0),
            "scope_prose_review_leads":local_m["scope_review_leads"]})
        if i%10==0 or i==len(choices):
            print(f"SOURCE SECTION CHECKPOINT {i}/{len(choices)}; CANDIDATES {len(seen)}",flush=True)
    assert len(seen)==selection["candidate_count"]
    manifest={"schema":"maththm.two-complete-chapters.manifest.v1",
       "source_revision":REV,"source_chapters":[chapters[n][0] for n in PAIR],
       "chapter_order":list(PAIR),"sections":len(choices),"section_inventory":inventory_rows,
       "active_candidate_count":len(seen),"source_lines":selection["source_lines"],
       "source_events_by_kind":dict(event_counts),
       "complete_source_chapters":True,"all_sections_consecutive_and_complete":True,
       "chapter_specific_context_reset_required":True,"proofs_reviewed":0,
       "final_equivalence_approved":0,"pass3_eligible":0,"published":0}
    write(ROOT/"MANIFEST.json",manifest)
    return manifest

def extract(manifest):
    contexts.ROOT=ROOT
    contexts.main()
    source_context=hp.read_jsonl(ROOT/"SHARED_CONTEXT_EXCERPTS.jsonl")
    # Scope signals are leads, not automatically inherited standing assumptions.
    leads=[q for q in source_context if q["kind"]=="unadjudicated_prose"]
    write(ROOT/"SCOPE_LEADS.json",{
        "source_revision":REV,"unadjudicated_lead_count":len(leads),
        "automatically_inherited_hypotheses":0,
        "note":"All durable section/chapter premise signals require semantic review; no prior lemma assumptions survive their closing environment.",
        "leads":[{"section_key":x["section_key"],"source_filename":x["source_filename"],
                  "source_start_line":x["source_start_line"],"signal":x["signal"],
                  "source_url":x["source_url"]} for x in leads]})
    return source_context

def draft(manifest,source_context):
    named=[x for x in source_context if x["kind"] in KINDS]
    leads_by_section={}
    for x in source_context:
        if x["kind"]=="unadjudicated_prose":
            leads_by_section.setdefault(x["section_key"],[]).append(x)
    all_ids=set()
    counts=Counter()
    shapes=Counter()
    results=[]
    previous=None
    chapter_durable_leads=[]
    for s in manifest["section_inventory"]:
        key=s["key"]
        file=s["source_filename"]
        changed=previous is not None and previous!=file
        if changed:
            chapter_durable_leads=[] # discharge all chapter-local assumptions
        previous=file
        packets=hp.read_jsonl(ROOT/f"{key}_packets.jsonl")
        events=hp.read_jsonl(ROOT/f"{key}_events.jsonl")
        frames=local_frames(events)
        rows=[]
        for p in packets:
            ident=p["candidate_id"]
            assert ident not in all_ids
            all_ids.add(ident)
            orig=p["statement_tex"]
            display=r300.clean_source(orig)
            shape,hyp,conc,items,aux,holds=r300.source_logical_shape(
                display,orig,p["prior_hypotheses"],p["prior_conclusions"])
            refs=list(dict.fromkeys(r300.REF.findall(display)))
            if refs:
                holds.append("Unexpanded source cross-reference labels: "+", ".join(refs[:15]))
            if p["statement_truncated"]:
                holds.append("Source packet truncates a statement; restore full statement before approval.")
            if r300.FOOTNOTE.search(display):
                holds.append("Source footnote may contain mathematical conditions.")
            if r300.DEICTIC.search(display) or r300.STRONG_AMBIGUITY.search(display):
                holds.append("Source refers to external or earlier contextual assumptions/notation.")
            if not p["prior_hypotheses"] and shape=="plain_source_statement":
                holds.append("Quantifier/hypothesis identification requires manual source-equivalence review.")
            if not p["prior_conclusions"] and shape=="plain_source_statement":
                holds.append("Consequent identification requires manual source-equivalence review.")
            # Persistent prose is NEVER made true by merely being scanned.
            preceding=[x for x in leads_by_section.get(key,[]) if
                       x["source_start_line"]<=p["source_statement_line"]]
            durable=[x for x in preceding+chapter_durable_leads if x["signal"]=="potential_durable_scope_change"]
            if durable:
                holds.append("Unadjudicated potentially durable source context; determine start/end and whether it applies.")
            loc=frames[p["source_statement_line"]]
            available=[x["label"] for x in named if x["label"] and (
                (x["source_filename"]==file and x["source_end_line"]<p["source_statement_line"]) or
                (x["source_filename"]==manifest["source_chapters"][0] and file==manifest["source_chapters"][1]))]
            if p["explicit_refs"] and any(x.get("error") for x in p["explicit_refs"]):
                holds.append("Unresolved referenced definition/situation label.")
            status=HOLD if holds else READY
            row={
               "schema":"maththm.two-complete-chapters.standalone-editorial-draft.v1",
               "candidate_id":ident,"source_revision":REV,
               "source_filename":file,"source_statement_line":p["source_statement_line"],
               "source_label":p["source_label"],"source_url":p["source_url"],
               "section_key":key,"section_index":s["section_index"],
               "section_title":s["section_title"],
               "section_start_line":s["section_start_line"],
               "section_end_line":s["section_end_line"],
               "chapter_order":s["chapter_order"],
               "source_formal_environment":loc["environment"],
               "source_formal_environment_start_line":loc["source_start"],
               "source_formal_environment_end_line":loc["source_end"],
               "original_source_statement_tex":orig,
               "standalone_statement_tex":display,
               "draft_hypotheses":hyp,"draft_conclusions":conc,
               "additional_conclusions":aux,
               "source_logical_form":shape,
               "source_enumerated_clauses":items,
               "applicable_prior_named_definition_ids":available,
               "named_definitions_are_not_ambient_assumptions":True,
               "section_ambient_hypotheses_auto_inherited":[],
               "local_lemma_hypotheses_expire_at_end":True,
               "source_named_reference_labels":[x["reference"] for x in p["explicit_refs"]],
               "source_inline_reference_labels":refs,
               "context_resolution_needed":list(dict.fromkeys(holds)),
               "context_review_status":status,
               "original_pass2_hypotheses_proposed":p["prior_hypotheses"],
               "original_pass2_conclusions_proposed":p["prior_conclusions"],
               "final_mathematical_source_equivalence_approved":False,
               "source_proof_screened":False,"pass3_eligible":False,"published":False,
               "original_pass1_pass2_unchanged":True,
               "inherited_context_review_decision":("chapter-local context discharged at boundary"
                  if changed else "only source definitions available, no unreviewed premises imported")
            }
            rows.append(row)
            counts[status]+=1
            shapes[shape]+=1
        hp.atomic_text(ROOT/f"{key}_reviews.jsonl","".join(
            json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n" for x in rows))
        results.append({"key":key,"chapter":file,"section_title":s["section_title"],
            "active_candidates":len(rows),
            "draft_ready":sum(x["context_review_status"]==READY for x in rows),
            "context_held":sum(x["context_review_status"]==HOLD for x in rows),
            "section_complete":True})
        # Keep unresolved potentially chapter-durable signals on the review stack.
        chapter_durable_leads.extend(x for x in leads_by_section.get(key,[])
                                     if x["signal"]=="potential_durable_scope_change")
    assert len(all_ids)==manifest["active_candidate_count"]
    out={"schema":"maththm.two-complete-chapters.editorial-drafts.v1",
         "source_revision":REV,"source_chapters":manifest["source_chapters"],
         "consecutive_complete_source_sections":manifest["sections"],
         "distinct_active_candidates_with_drafts":len(all_ids),
         "status_counts":dict(counts),"logical_forms":dict(shapes),
         "section_results":results,
         "final_mathematical_source_equivalence_approvals":0,
         "proofs_screened":0,"pass3_eligible":0,"published":0,
         "quality_note":"Draft-ready is a preliminary syntactic/context flag, not independent mathematical source-equivalence verification. Holds are conservative."}
    write(ROOT/"DRAFT_MANIFEST.json",out)
    return out

def validate_and_register(manifest,draft_manifest,context):
    selection=json.loads((ROOT/"SELECTION.json").read_text())
    assert selection["all_source_sections_included"] and len(selection["chapters"])==2
    assert manifest["sections"]==len(selection["sections"])
    assert draft_manifest["distinct_active_candidates_with_drafts"]==selection["candidate_count"]
    assert sum(draft_manifest["status_counts"].values())==selection["candidate_count"]
    assert manifest["source_events_by_kind"]["enter_local_environment"]==manifest["source_events_by_kind"]["exit_local_environment"]
    registry=json.loads(REGISTRY.read_text())
    assert registry["source_revision"]==REV
    used={(x["source_file"],x["section_start_line"]) for x in registry["sections"]}
    checkpoints=[]
    seen=set()
    previous=None
    cumulative=0
    for s in manifest["section_inventory"]:
        key=s["key"]
        file=s["source_filename"]
        assert (file,s["section_start_line"]) not in used
        entered=[]
        events=hp.read_jsonl(ROOT/f"{key}_events.jsonl")
        packets=hp.read_jsonl(ROOT/f"{key}_packets.jsonl")
        rows=hp.read_jsonl(ROOT/f"{key}_reviews.jsonl")
        assert len(packets)==len(rows)==s["active_candidate_count"]
        assert sum(e["kind"]=="candidate_location" for e in events)==len(rows)
        for e in events:
            if e["kind"]=="enter_local_environment":
                entered.append(e["environment"])
            elif e["kind"]=="exit_local_environment":
                assert entered and entered.pop()==e["environment"]
        assert not entered,key
        assert {x["candidate_id"] for x in packets}=={x["candidate_id"] for x in rows}
        for row in rows:
            assert row["candidate_id"] not in seen
            seen.add(row["candidate_id"])
            assert row["draft_hypotheses"] and row["draft_conclusions"]
            assert row["original_source_statement_tex"]
            assert row["standalone_statement_tex"]
            assert row["local_lemma_hypotheses_expire_at_end"]
            assert not row["section_ambient_hypotheses_auto_inherited"]
            assert not row["final_mathematical_source_equivalence_approved"]
            assert not row["source_proof_screened"] and not row["pass3_eligible"] and not row["published"]
        reset=previous is not None and previous!=file
        if previous is not None and previous==file:
            prev=checkpoints[-1]
            assert prev["section_end_line"]+1==s["section_start_line"]
        previous=file
        cumulative+=len(rows)
        checkpoints.append({"schema":"maththm.two-complete-chapters.checkpoint.v1",
            "source_revision":REV,"section_key":key,"source_filename":file,
            "section_start_line":s["section_start_line"],"section_end_line":s["section_end_line"],
            "completed_active_candidates_this_section":len(rows),
            "cumulative_completed_active_candidates":cumulative,
            "chapter_boundary_reset_applied":reset,
            "source_local_hypothesis_stack_at_end":[],
            "chapter_ambient_hypotheses_auto_inherited":[],
            "full_section_traversed_even_if_no_active_candidates":True,
            "completed_active_candidate_ids":[x["candidate_id"] for x in rows],
            "proof_bodies_reviewed":False,
            "final_source_equivalence_approved":False,
            "safe_to_restart_at_next_complete_section":True})
    assert len(seen)==selection["candidate_count"]
    assert sum(x["chapter_boundary_reset_applied"] for x in checkpoints)==1
    assert len(checkpoints)==selection["section_count"]
    assert checkpoints[0]["source_filename"]==selection["chapters"][0]["source_filename"]
    assert checkpoints[-1]["source_filename"]==selection["chapters"][1]["source_filename"]
    assert checkpoints[0]["section_start_line"]==selection["sections"][0]["section_start_line"]
    assert checkpoints[-1]["section_end_line"]==selection["sections"][-1]["section_end_line"]
    hp.atomic_text(ROOT/"SECTION_CHECKPOINTS.jsonl","".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in checkpoints))
    write(ROOT/"VALIDATION.json",{"passed":True,"chapters":manifest["source_chapters"],
       "sections":len(checkpoints),"candidates":len(seen),
       "source_environment_frames_balanced":True,"no_registry_overlap":True,
       "both_chapters_whole":True,"candidate_identity_unique":True,
       "chapter_reset_applied":True,"source_equivalence_approvals":0,
       "proofs_screened":0,"published":0})
    # Registry mutation occurs only after every section and candidate validates.
    for s in manifest["section_inventory"]:
        registry["sections"].append({"source_file":s["source_filename"],
           "section_start_line":s["section_start_line"],
           "section_end_line":s["section_end_line"],
           "active_candidate_count":s["active_candidate_count"],
           "review_level":"standalone_drafts_without_final_source_equivalence",
           "artifacts":f"{ROOT}/{s['key']}_reviews.jsonl",
           "batch":BATCH})
    registry["sections_completed_for_draft"]=len(registry["sections"])
    registry["active_candidate_drafts_in_these_sections"]=sum(
        x["active_candidate_count"] for x in registry["sections"])
    write(REGISTRY,registry)
    report=f"""# Two complete adjacent Stacks chapters — draft reconstruction

Pinned source: \`{REV}\`

- Chapters: **{manifest['source_chapters'][0]}** and **{manifest['source_chapters'][1]}** (source chapters 32 and 33).
- Fully processed source sections: **{manifest['sections']}**. No section skipped or truncated.
- Source lines traversed: **{manifest['source_lines']:,}**.
- Distinct active canonical candidates drafted: **{manifest['active_candidate_count']}**.
- Preliminary draft-ready (pending mathematical equivalence review): **{draft_manifest['status_counts'].get(READY,0)}**.
- Held for source-context/logic review: **{draft_manifest['status_counts'].get(HOLD,0)}**.
- Named source context records: **{sum(q['kind'] in KINDS for q in context)}**.
- Unadjudicated source prose/scope leads: **{sum(q['kind']=='unadjudicated_prose' for q in context)}**.
- Complete-section checkpoints: **{len(checkpoints)}**.
- Cumulative section-draft registry: **{registry['sections_completed_for_draft']}** sections and **{registry['active_candidate_drafts_in_these_sections']}** candidates.

Every statement retains the source text, source URL, provisional logical split and
specific holds. Potentially durable prose assumptions are flagged and NOT
inherited automatically; theorem/lemma hypotheses expire at formal closure;
chapter-specific premise scope resets between chapters. Named definitions
remain usable as terminology only.

**Not performed:** independent mathematical source-equivalence verification,
proof correctness checks, Pass 3 screening, or publication. A draft-ready
status is not a truth certificate.

Reproduce with \`python -m scripts.stacks_two_complete_chapters\` after
checking out the pinned Stacks source in \`upstream/stacks\`; this command
refuses an overlapping new batch and is not a registered-batch replay mode.
"""
    hp.atomic_text(ROOT/"REPORT.md",report)
    return registry

def main():
    manifest=stage()
    context=extract(manifest)
    drafts=draft(manifest,context)
    registry=validate_and_register(manifest,drafts,context)
    print(json.dumps({"chapters":manifest["source_chapters"],
       "sections":manifest["sections"],"active_candidates":manifest["active_candidate_count"],
       "statuses":drafts["status_counts"],"cumulative_drafts":registry["active_candidate_drafts_in_these_sections"]}),flush=True)

if __name__=="__main__":
    main()

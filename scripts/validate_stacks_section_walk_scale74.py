#!/usr/bin/env python3
"""Validate all five *complete* Morphisms sections in scale-74 pilot.

Structural/provenance/scope checks, NOT theorem truth or proof verification.
The reviewer-made drafts remain on separate files with final gate closed.
"""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.active_candidate_pool import IDS
from scripts.stacks_context_recon import REV

ROOT=Path("harvest/section_walk_scale74_2026-10-28")
SECTIONS=[
    ("affine",1710,2110,13),
    ("quasi_finite",3522,4053,17),
    ("syntomic",5718,6136,14),
    ("differentials",6337,6858,15),
    ("unramified",7603,8033,15),
]
READY="standalone_draft_ready_for_validation"
HOLD="context_resolution_pending"

def main():
    manifest=json.loads((ROOT/"MANIFEST.json").read_text())
    assert manifest["source_revision"]==REV
    assert manifest["section_count"]==5
    assert manifest["actual_candidate_count"]==74
    assert len(SECTIONS)==len(manifest["sections"])
    active=p.load_rows(IDS,"candidate_id")
    assert len(active)==9675
    sections=[]
    checkpoints=[]
    all_seen=set()
    statuses=Counter()
    kinds=Counter()
    total_source_lines=0
    total_events=Counter()
    total_reference_uses=0
    for ix,(key,start,end,expected) in enumerate(SECTIONS):
        sub=next(x for x in manifest["sections"]
                 if x["section_start"]==start)
        assert sub["section_end"]==end
        assert sub["candidate_count"]==expected
        packets=p.load_rows(ROOT/(key+"_packets.jsonl"),"candidate_id")
        reviews=p.load_rows(ROOT/(key+"_reviews.jsonl"),"source_candidate_id")
        events=p.read_jsonl(ROOT/(key+"_events.jsonl"))
        assert len(packets)==len(reviews)==expected
        assert set(packets)==set(reviews)
        assert set(reviews).issubset(active)
        assert not (all_seen & set(reviews))
        all_seen|=set(reviews)
        stack=[]
        lemma_count=0
        candidate_event_count=0
        local_end_lines=[]
        beginnings=[]
        for e in events:
            total_events[e["kind"]]+=1
            if e["kind"]=="enter_local_environment":
                stack.append((e["environment"],e["line"]))
            elif e["kind"]=="exit_local_environment":
                assert stack and stack[-1][0]==e["environment"],(key,e,stack)
                kind,begin=stack.pop()
                assert begin<=e["line"]
                if kind=="lemma":
                    local_end_lines.append(e["line"])
                    lemma_count+=1
            elif e["kind"]=="candidate_location":
                assert stack and stack[-1][0]=="lemma",(key,e,stack)
                candidate_event_count+=1
                beginnings.append(e["line"])
        assert not stack,(key,stack)
        assert lemma_count==candidate_event_count==expected
        assert len(local_end_lines)==expected
        assert all(beginnings[i]<local_end_lines[i] for i in range(expected))
        sorted_reviews=sorted(reviews.values(),key=lambda v:v["source_line"])
        assert [r["source_line"] for r in sorted_reviews]==beginnings
        section_kind=Counter()
        for i,(src,rev) in enumerate(zip(
            sorted(packets.values(),key=lambda x:x["source_statement_line"]),
            sorted_reviews
        )):
            ident=rev["source_candidate_id"]
            assert src["candidate_id"]==ident
            assert src["source_label"]==rev["source_label"]
            assert src["source_statement_line"]==rev["source_line"]
            assert src["source_revision"]==rev["source_revision"]==REV
            assert rev["section_key"]==key
            assert rev["source_url"].startswith(
                "https://github.com/stacks/stacks-project/blob/"+REV+"/")
            assert rev["review_order"]==i+1
            assert rev["explicit_hypotheses"],ident
            assert rev["conclusions"] or rev["equivalent_conditions"],ident
            assert rev["standalone_statement_latex"].strip()
            assert rev["local_hypotheses_expire"] is True
            assert rev["scope_reviewed"] is True
            assert rev["source_equivalence_final_approved"] is False
            assert rev["proofs_screened"] is False
            assert rev["published"] is False
            assert rev["original_pass2_unchanged"] is True
            assert rev["review_status"] in (READY,HOLD)
            if rev["review_status"]==READY:
                assert not rev["unresolved_context"],ident
                assert r"\ref{" not in rev["standalone_statement_latex"],ident
            else:
                assert rev["unresolved_context"]
            for ref in rev["context_definitions_available"]:
                cutoff=ref.get("only_after_line",ref.get("from",ref.get("line",0)))
                # A potential later-source definition can be indexed as a
                # future reference but MUST NOT be considered active early.
                assert cutoff<=rev["source_line"] or "only_after_line" in ref
            if key=="differentials":
                # Notation is active only AFTER the real 'from now on'
                # declaration on line 6404, not for its two predecessors.
                has_note=any(
                    r["label"]=="morphisms-notation-differential-restriction"
                    for r in rev["context_definitions_available"])
                assert has_note==(rev["source_line"]>=6404)
            statuses[rev["review_status"]]+=1
            kinds[rev["logical_form"]]+=1
            section_kind[rev["review_status"]]+=1
            total_reference_uses+=len(src["explicit_refs"])
        if key=="differentials":
            leads=[e for e in events if e["kind"]=="potential_durable_scope_change"]
            assert len(leads)==1 and leads[0]["line"]==6404,leads
            scope=json.loads((ROOT/"differentials_scopes.json").read_text())
            notes=[x for x in scope["scope_declarations"] if x["kind"]=="notation_override"]
            assert len(notes)==1
            assert notes[0]["scope_start"]==6404 and notes[0]["scope_end"]==end
            assert notes[0]["applies_as_added_hypothesis"] is False
        else:
            assert not any(e["kind"]=="potential_durable_scope_change"
                           for e in events),(key,"unreviewed durable signal")
        checkpoints.append({
            "schema":"maththm.section-walk-complete-section-checkpoint.v1",
            "source_revision":REV,
            "completed_section_file":"morphisms.tex",
            "section_key":key,
            "section_label":sub["section_label"],
            "section_start_line":start,
            "section_end_line":end,
            "next_uninspected_source_line":end+1,
            "source_intervening_sections_not_assumed_reviewed":True,
            "completed_source_candidate_ids":[v["source_candidate_id"]
                                             for v in sorted_reviews],
            "candidate_count":expected,
            "review_status_counts":dict(section_kind),
            "local_lemma_scope_frames_popped":expected,
            "active_lemma_local_assumptions_at_checkpoint":[],
            "persistent_section_hypotheses_at_checkpoint":[],
            "section_specific_notation_must_expire_before_next_section":True,
            "named_source_definitions_available_as_references":sorted(
                {r["label"] for v in sorted_reviews
                 for r in v["context_definitions_available"]}),
            "no_external_proofs_read":True,
            "proofs_not_screened":True,
            "whole_section_complete":True
        })
        total_source_lines+=end-start+1
        sections.append({
            "section_key":key,"start_line":start,"end_line":end,
            "section_title":sub["section_title"],
            "candidates":expected,
            "review_status_counts":dict(section_kind),
            "local_lemma_scope_frames_popped":expected,
            "source_lines":end-start+1,
            "event_counts":dict(Counter(e["kind"] for e in events)),
        })
    assert len(all_seen)==74
    assert statuses[READY]+statuses[HOLD]==74
    assert statuses[READY]>=50
    assert len(checkpoints)==5 and all(x["whole_section_complete"] for x in checkpoints)
    p.atomic_text(ROOT/"SECTION_CHECKPOINTS.jsonl",
        "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in checkpoints))
    result={
        "schema":"maththm.section-walk-scale74-validation.v1",
        "source_revision":REV,
        "chapter":"morphisms.tex",
        "complete_sections_processed":5,
        "all_sections_completed_without_split":True,
        "distinct_original_candidate_ids":len(all_seen),
        "source_lines_scanned":total_source_lines,
        "reviewed_standalone_drafts":74,
        "status_counts":dict(sorted(statuses.items())),
        "reviewed_nontrivial_logical_forms":dict(sorted(kinds.items())),
        "exact_source_label_reference_uses":total_reference_uses,
        "scope_event_counts":dict(sorted(total_events.items())),
        "temporary_lemma_frames_popped":74,
        "mid_section_notation_scope_changes_adjudicated":1,
        "complete_section_checkpoints":5,
        "all_source_equivalence_approvals":0,
        "all_proofs_screened":0,
        "pass3_eligible":0,
        "original_source_pass1_pass2_changed":False,
        "published_theorems_changed":False,
        "provisional_duplicate_decisions_changed":False,
        "sections":sections,
        "limitations":[
          "Source-order events and semantic draft reviews are not proofs.",
          "A draft-ready status is not final mathematical source equivalence validation.",
          "These five sections are nonconsecutive within one chapter; assumptions in skipped sections were not automatically inherited.",
          "Global/chapter conventions and named definitions are available as context references but not automatically imported as extra hypotheses.",
          "If future samples show internal context changes, scope adjudication must precede use.",
          "No wall-clock A/B benchmark or safe cap has yet been established."
        ]
    }
    p.atomic_text(ROOT/"VALIDATION.json",json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in (
        "complete_sections_processed","distinct_original_candidate_ids",
        "source_lines_scanned","status_counts","temporary_lemma_frames_popped",
        "mid_section_notation_scope_changes_adjudicated")},sort_keys=True))
    return result

if __name__=="__main__":
    main()

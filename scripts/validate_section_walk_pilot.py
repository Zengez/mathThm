#!/usr/bin/env python3
"""Validate scoped section walk + human-written standalone overlays.

This enforces environment push/pop and provenance without claiming to
verify theorems or proofs. Only the event stream and source statements
were scanned; no proof bodies were interpreted.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.stacks_context_recon import REV

BASE=Path("harvest")
EVENTS=BASE/"SECTION_WALK_PILOT_EVENTS_2026-10-28.jsonl"
PACKETS=BASE/"SECTION_WALK_PILOT_PACKETS_2026-10-28.jsonl"
REVIEWS=BASE/"SECTION_WALK_PILOT_STANDALONE_REVIEWS_2026-10-28.jsonl"
CHECKPOINTS=BASE/"SECTION_WALK_PILOT_CONTEXT_CHECKPOINTS_2026-10-28.jsonl"
METRICS=BASE/"SECTION_WALK_PILOT_VALIDATION_2026-10-28.json"
SHARED_DEFINITION="morphisms-definition-flat"
OUTPUT_MARKER="mathematical_source_context_reviewed_not_proof_checked"

def validate():
    events=p.read_jsonl(EVENTS)
    packets=p.load_rows(PACKETS,"candidate_id")
    reviews=p.load_rows(REVIEWS,"candidate_id")
    assert len(packets)==len(reviews)==15
    assert {x["source_statement_line"] for x in reviews.values()}=={
        x["source_statement_line"] for x in packets.values()}
    assert len(set(x["source_label"] for x in reviews.values()))==15
    all_ids=set(reviews)
    stack=[]
    named_defs=[]
    seen=set()
    checks=[]
    entering=Counter()
    leaving=Counter()
    candidate_scopes=[]
    lemma_end_lines=[]
    for event in events:
        kind=event["kind"]
        if kind=="enter_local_environment":
            stack.append({"kind":event["environment"],"line":event["line"]})
            entering[event["environment"]]+=1
        elif kind=="exit_local_environment":
            assert stack and stack[-1]["kind"]==event["environment"],(stack,event)
            prior=stack.pop()
            leaving[event["environment"]]+=1
            if prior["kind"]=="lemma":
                lemma_end_lines.append(event["line"])
            if prior["kind"]=="definition" and prior["line"]==4639:
                named_defs.append({"kind":"definition","label":"definition-flat",
                                   "source_url":"https://github.com/stacks/stacks-project/blob/"
                                    +REV+"/morphisms.tex#L4639",
                                    "persistent_as_reference":True,
                                    "persistent_as_hypothesis":False})
        elif kind=="candidate_location":
            assert len(stack)==1 and stack[0]["kind"]=="lemma",(event,stack)
            matching=[r for r in reviews.values() if r["source_statement_line"]==event["line"]]
            assert len(matching)==1, event
            row=matching[0]
            assert row["candidate_id"] not in seen
            seen.add(row["candidate_id"])
            assert len(named_defs)==1 and named_defs[0]["label"]=="definition-flat"
            assert row["shared_context_label"]==SHARED_DEFINITION
            assert row["source_filename"]=="morphisms.tex"
            assert row["source_revision"]==REV
            assert row["candidate_pass3_eligible"] is False
            assert row["published"] is False
            assert row["proof_correctness_reviewed"] is False
            assert row["final_source_equivalence_approved"] is False
            assert row["original_pass2_unchanged"] is True
            assert not row["effective_unconditional_section_hypotheses"]
            assert row["explicit_hypotheses"]
            assert row["standalone_statement_latex"]
            assert r"\ref{" not in row["standalone_statement_latex"]
            assert row["conclusion_claims"] or row["equivalent_conditions"]
            assert row["local_hypotheses_expire_at_environment_end"]
            if row["equivalent_conditions"]:
                assert len(row["equivalent_conditions"])==4
            assert row["source_label"]==packets[row["candidate_id"]]["source_label"]
            candidate_scopes.append({
                "candidate_id":row["candidate_id"],
                "source_line":event["line"],
                "source_label":row["source_label"],
                "effective_section_hypotheses":[],
                "in_scope_lemma_hypotheses":row["explicit_hypotheses"],
                "available_source_definitions":[SHARED_DEFINITION],
                "unresolved_scope_changes":[],
                "scope_stack":["section","lemma"],
                "proof_unread":True,
                "status":row["standalone_context_status"],
            })
        elif kind=="potential_durable_scope_change":
            raise AssertionError("No unreviewed durable context signals in this section")
        elif kind=="proof_skipped":
            assert not stack or stack[-1]["kind"]=="lemma"
    assert not stack, stack
    assert seen==all_ids
    assert len(candidate_scopes)==len(lemma_end_lines)==15
    assert all(end>candidate_scopes[i]["source_line"] for i,end in enumerate(lemma_end_lines))
    assert entering["definition"]==leaving["definition"]==1
    assert entering["lemma"]==leaving["lemma"]==15
    assert all("source_url" in x for x in named_defs)
    defn_reused=len(candidate_scopes)-len(named_defs)
    # The source section-wide context remains empty on exit. The shared
    # definition is available by label but no individual lemma's variables
    # persist into subsequent lemmas.
    checkpoints=[]
    for idx,x in enumerate(candidate_scopes):
        checkpoints.append({
            "section_id":"morphisms:section-flat",
            "after_candidate_id":x["candidate_id"],
            "last_completed_environment_end_line":lemma_end_lines[idx],
            "resume_source_line_after_environment":lemma_end_lines[idx]+1,
            "next_statement_line":lemma_end_lines[idx]+1,
            "active_local_environment_hypotheses":[],
            "effective_section_hypotheses":[],
            "available_named_source_definitions":named_defs,
            "completed_candidate_ids":[z["candidate_id"] for z in candidate_scopes
                                     if z["source_line"]<=x["source_line"]],
            "inherited_source_revision":REV,
            "proofs_unread":True,
            "safe_to_resume_without_reusing_lemma_hypotheses":True,
        })
    p.atomic_text(CHECKPOINTS,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)
                                      +"\n" for x in checkpoints))
    metrics={
        "schema":"maththm.section-walk-scoped-pilot-review.v1",
        "source_revision":REV,
        "chapter":"morphisms.tex","section_title":"Flat morphisms",
        "section_start_line":4615,"section_end_line":4994,
        "active_candidates_in_section":15,
        "candidate_standalone_drafts":len(reviews),
        "candidate_context_reviewed":len(reviews),
        "final_standalone_source_equivalence_approvals":0,
        "proof_reviews":0,
        "pass3_eligible":0,
        "named_definition_interpreted_once":1,
        "named_definition_reuse_opportunities":defn_reused,
        "local_lemma_frames_pushed_and_popped":15,
        "source_section_durable_hypotheses":0,
        "durable_scope_changes_unresolved":0,
        "checkpoint_count":len(checkpoints),
        "scope_events":dict(Counter(x["kind"] for x in events)),
        "equivalence_results_preserved_as_equivalences":sum(
            bool(x["equivalent_conditions"]) for x in reviews.values()),
        "other_nontrivial_conclusion_addenda_preserved":sum(
            bool(x["additional_conclusions"]) for x in reviews.values()),
        "duplicate_or_proof_records_modified":False,
        "active_candidates_modified":False,
        "note":"All source-context drafts require final source-equivalence judgement; no correctness/proof or publication claim.",
        "staged_for_review_only":True,
    }
    p.atomic_text(METRICS,json.dumps(metrics,indent=2,sort_keys=True)+"\n")
    print(json.dumps(metrics,sort_keys=True))
    return metrics

if __name__=="__main__":
    validate()

#!/usr/bin/env python3
"""Validate complete consecutive source sections, 300 draft overlays and scoping.

No theorem proof screened, no final semantic equivalence certificate. The
output checkpoints are safe at section boundaries, including a chapter reset.
"""
from __future__ import annotations
import json,re
from pathlib import Path
from collections import Counter
from scripts import harvest_pipeline as hp
from scripts.active_candidate_pool import IDS
from scripts.stacks_context_recon import REV
from scripts.stacks_consecutive_section_window150 import completed_section_starts

ROOT=Path("harvest/section_walk_scale300_2026-10-28")
READY="standalone_draft_ready_for_validation"
HOLD="context_resolution_pending"
FORMAL={"lemma","proposition","theorem","corollary"}

def main():
    m=json.loads((ROOT/"MANIFEST.json").read_text(encoding="utf-8"))
    draft=json.loads((ROOT/"DRAFT_MANIFEST.json").read_text(encoding="utf-8"))
    scope=json.loads((ROOT/"SCOPES_REVIEWED.json").read_text(encoding="utf-8"))
    defs=hp.read_jsonl(ROOT/"SHARED_CONTEXT_EXCERPTS.jsonl")
    named=[x for x in defs if x["kind"] in (
        "definition","situation","notation","setup","construction")]
    active=hp.load_rows(IDS,"candidate_id")
    assert len(active)==9675
    assert m["source_revision"]==draft["source_revision"]==scope["source_revision"]==REV
    assert m["all_chapters_adjacent_in_source_order"]
    assert m["all_sections_consecutive_and_complete"]
    assert m["source_chapters"]==draft["source_chapters"]==[
        "coherent.tex","divisors.tex"]
    assert m["sections"]==draft["consecutive_complete_source_sections"]==54
    assert m["active_candidate_count"]==draft["distinct_active_candidates_with_drafts"]==300
    assert len(scope["section_context_leads"])==8
    assert len(scope["named_context_with_nonformal_definition"])==2
    assert len(named)==35,len(named)
    assert all(x["available_as_terminology_only"] for x in named)
    assert all(x["never_import_local_definition_variables_as_theorem_premises"] for x in named)
    assert m["source_events_by_kind"]["proof_skipped"]==311
    assert m["source_events_by_kind"]["candidate_location"]==300
    assert m["source_events_by_kind"]["enter_local_environment"]==m["source_events_by_kind"]["exit_local_environment"]==364
    seen=set()
    status=Counter()
    forms=Counter()
    checks=[]
    checkpoints=[]
    previous=None
    running=0
    entered=Counter()
    exited=Counter()
    extra_source_formals=0
    excluded=completed_section_starts()
    # Once the successful batch is registered, allow revalidation of its
    # own sections; reject only overlap with *other* completed batches.
    registry_file=Path("harvest/SECTION_WALK_COMPLETED_SECTIONS.json")
    if registry_file.exists():
        registry=json.loads(registry_file.read_text(encoding="utf-8"))
        for old in registry.get("sections",[]):
            if old.get("batch")=="scale300_2026-10-28":
                excluded.setdefault(old["source_file"],set()).discard(old["section_start_line"])
    for s in m["section_inventory"]:
        key=s["key"]
        file=s["source_filename"]
        start,end=s["section_start_line"],s["section_end_line"]
        assert start not in excluded.get(file,set()),key
        if previous is not None:
            if previous["source_filename"]==file:
                assert previous["section_end_line"]+1==start
            else:
                assert previous["source_filename"]=="coherent.tex"
                assert previous["section_index"]==17
                assert file=="divisors.tex" and s["section_index"]==18
                assert start==17 # First section of adjoining chapter.
        prev_chapter=previous["source_filename"] if previous is not None else None
        chapter_reset=prev_chapter is not None and prev_chapter!=file
        previous=s
        source=hp.load_rows(ROOT/(key+"_packets.jsonl"),"candidate_id")
        reviews=hp.load_rows(ROOT/(key+"_reviews.jsonl"),"candidate_id")
        events=hp.read_jsonl(ROOT/(key+"_events.jsonl"))
        assert len(source)==len(reviews)==s["active_candidate_count"],key
        assert set(source)==set(reviews)
        assert set(reviews).issubset(active)
        assert not(set(reviews)&seen)
        seen.update(reviews)
        stack=[]
        candidate_event_lines=[]
        formal_env_lines=[]
        all_source_formals=0
        for ev in events:
            typ=ev["kind"]
            if typ=="enter_local_environment":
                stack.append((ev["environment"],ev["line"]))
                entered[ev["environment"]]+=1
                if ev["environment"] in FORMAL:
                    formal_env_lines.append(ev["line"])
                    all_source_formals+=1
            elif typ=="exit_local_environment":
                assert stack and stack[-1][0]==ev["environment"],(key,stack,ev)
                stack.pop()
                exited[ev["environment"]]+=1
            elif typ=="candidate_location":
                assert stack and stack[-1][0] in FORMAL
                candidate_event_lines.append(ev["line"])
        assert not stack,key
        assert len(candidate_event_lines)==len(reviews)
        assert set(candidate_event_lines).issubset(set(formal_env_lines))
        extra_source_formals+=all_source_formals-len(candidate_event_lines)
        assert candidate_event_lines==sorted(v["source_statement_line"] for v in source.values())
        for ident,r in reviews.items():
            raw=source[ident]
            assert ident==raw["candidate_id"]==r["candidate_id"]
            assert r["source_filename"]==file
            assert r["source_statement_line"]==raw["source_statement_line"]
            assert r["source_label"]==raw["source_label"]
            assert r["source_url"]==raw["source_url"]
            assert r["original_source_statement_tex"]==raw["statement_tex"]
            assert r["source_revision"]==REV
            assert r["section_key"]==key
            assert r["section_index"]==s["section_index"]
            assert r["section_start_line"]==start
            assert r["section_end_line"]==end
            assert start<=r["source_formal_environment_start_line"]<=r["source_statement_line"]<r["source_formal_environment_end_line"]<=end
            assert r["source_formal_environment"] in FORMAL
            assert r["standalone_statement_tex"].strip()
            assert r["draft_hypotheses"]
            assert r["draft_conclusions"]
            assert not r["section_ambient_hypotheses_auto_inherited"]
            assert r["named_definitions_are_not_ambient_assumptions"]
            assert r["local_lemma_hypotheses_expire_at_end"]
            assert r["context_review_status"] in (HOLD,READY)
            assert not r["final_mathematical_source_equivalence_approved"]
            assert not r["source_proof_screened"] and not r["pass3_eligible"] and not r["published"]
            assert r["original_pass1_pass2_unchanged"]
            assert r["source_named_reference_labels"]==[
                a["reference"] for a in raw["explicit_refs"]]
            available={
                z["label"] for z in named if z["label"] and (
                    (z["source_filename"]==file and
                     z["source_end_line"]<r["source_statement_line"])
                    or (file=="divisors.tex" and z["source_filename"]=="coherent.tex"))
            }
            assert set(r["applicable_prior_named_definition_ids"])==available,(ident,key)
            if r["context_review_status"]==READY:
                assert not r["context_resolution_needed"],ident
                assert r"\ref{" not in r["standalone_statement_tex"],ident
                assert r"\footnote{" not in r["standalone_statement_tex"],ident
                assert r["source_logical_form"] not in (
                    "alternative_conditional_cases",
                    "nested_or_multi_enumeration_needs_review",
                    "shared_existential_witness_hypotheses",
                    "shared_existential_witness_properties"),ident
            else:
                assert r["context_resolution_needed"]
            if r["source_logical_form"]=="equivalent_conditions":
                assert set(r["source_enumerated_clauses"]).issubset(set(r["draft_conclusions"])),ident
                assert not (set(r["source_enumerated_clauses"]) & set(r["draft_hypotheses"])),ident
            if r["source_logical_form"]=="listed_premises_then_conclusion":
                assert set(r["source_enumerated_clauses"]).issubset(set(r["draft_hypotheses"])),ident
            if r["source_logical_form"]=="shared_existential_witness_hypotheses":
                assert any(r"\begin{enumerate}" in h for h in r["draft_hypotheses"]),ident
                assert r["context_review_status"]==HOLD
            if r["source_logical_form"]=="nested_or_multi_enumeration_needs_review":
                assert r["context_review_status"]==HOLD
            forms[r["source_logical_form"]]+=1
            status[r["context_review_status"]]+=1
        running+=len(reviews)
        checkpoint={
            "schema":"maththm.scale300.complete-source-section-checkpoint.v1",
            "source_revision":REV,
            "section_key":key,
            "source_filename":file,
            "section_title":s["section_title"],
            "section_start_line":start,
            "section_end_line":end,
            "resume_after_section_end_line":end+1,
            "chapter_boundary_reset_applied":chapter_reset,
            "full_section_traversed_even_if_no_active_candidates":True,
            "source_lemma_scope_stack_at_end":[],
            "source_chapter_standing_premises_at_end":[],
            "available_named_source_definitions":[
                {"label":q["label"],"source_filename":q["source_filename"],
                 "line":q["source_start_line"],"role":"term_reference_not_hypothesis"}
                for q in named if q["label"] and (
                    (q["source_filename"]==file and q["source_end_line"]<=end)
                    or (file=="divisors.tex" and q["source_filename"]=="coherent.tex"))],
            "completed_active_candidate_ids":[v["candidate_id"]
                for v in sorted(reviews.values(),key=lambda x:x["source_statement_line"])],
            "completed_active_candidates_this_section":len(reviews),
            "cumulative_completed_active_candidates":running,
            "proof_bodies_reviewed":False,
            "final_source_equivalence_approved":False,
            "safe_to_restart_at_next_complete_section":True
        }
        if chapter_reset:
            assert checkpoint["source_lemma_scope_stack_at_end"]==[]
            assert checkpoint["source_chapter_standing_premises_at_end"]==[]
        checkpoints.append(checkpoint)
        checks.append({
            "section_key":key,"file":file,"start":start,"end":end,
            "candidate_count":len(reviews),
            "ready":sum(x["context_review_status"]==READY for x in reviews.values()),
            "held":sum(x["context_review_status"]==HOLD for x in reviews.values()),
            "source_formal_statement_environments":all_source_formals,
            "scope_closed":True,
        })
    assert len(seen)==running==300
    assert len(checkpoints)==54
    assert sum(x["end"]-x["start"]+1 for x in checks)==14692
    assert sum(entered.values())==sum(exited.values())==364
    assert entered==exited
    assert status[READY]+status[HOLD]==300
    assert forms==draft["logical_forms"],(forms,draft["logical_forms"])
    assert dict(sorted(status.items()))==draft["status_counts"]
    assert checkpoints[16]["source_filename"]=="coherent.tex"
    assert checkpoints[17]["chapter_boundary_reset_applied"]
    assert checkpoints[17]["source_filename"]=="divisors.tex"
    assert checkpoints[17]["section_start_line"]==17
    assert checks[17]["candidate_count"]==0
    assert checkpoints[-1]["cumulative_completed_active_candidates"]==300
    assert all(q["safe_to_restart_at_next_complete_section"] for q in checkpoints)
    hp.atomic_text(ROOT/"SECTION_CHECKPOINTS.jsonl","".join(
         json.dumps(q,ensure_ascii=False,sort_keys=True)+"\n" for q in checkpoints))
    report={
        "schema":"maththm.scale300.whole-section-scope-integrity-validation.v1",
        "source_revision":REV,
        "chapters":m["source_chapters"],
        "source_sections_complete_consecutive":54,
        "source_section_lines":14692,
        "active_candidate_ids_with_drafts":300,
        "status_counts":dict(sorted(status.items())),
        "source_environment_frames_entered_and_closed":364,
        "additional_formal_statements_traversed_not_added_to_active_pool":extra_source_formals,
        "proof_environments_skipped_without_reading_bodies":311,
        "named_source_definition_contexts":35,
        "prose_scope_leads_adjudicated":8,
        "two_nonformal_section_concepts_reviewed":2,
        "named_definitions_available_only_after_source_position":True,
        "chapter_boundary_reset":True,
        "consecutive_completed_section_checkpoints":54,
        "logical_shapes":dict(sorted(forms.items())),
        "equivalence_clauses_not_inherited_as_premises":True,
        "listed_premise_clauses_not_promoted_to_conclusions":True,
        "shared_existential_witnesses_not_split":True,
        "all_temporarily_lemma_local_hypotheses_expired_at_lemma_end":True,
        "original_pass1_pass2_and_active_pool_unchanged":True,
        "public_theorem_catalog_unchanged":True,
        "final_mathematical_source_equivalence_approvals":0,
        "proofs_reviewed":0,
        "pass3_eligible":0,
        "sections":checks,
        "limitations":[
          "A source-grounded ready draft is not a final semantic-equivalence certificate.",
          "No proof has been checked and no candidate has been promoted to Pass 3.",
          "Other source cross-references and difficult logical scope cases remain explicit holds.",
          "Definitions are referenced by canonical source labels, not automatically copied as assumptions.",
          "No controlled runtime benchmark establishes an optimal batch cap."
        ],
    }
    hp.atomic_text(ROOT/"VALIDATION.json",json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in (
       "active_candidate_ids_with_drafts","status_counts",
       "source_sections_complete_consecutive",
       "source_section_lines","source_environment_frames_entered_and_closed",
       "additional_formal_statements_traversed_not_added_to_active_pool")}))
if __name__=="__main__":main()

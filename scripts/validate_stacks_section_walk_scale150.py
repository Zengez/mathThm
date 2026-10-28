#!/usr/bin/env python3
"""End-to-end section-contiguity, scoped-context, and standalone-overlay audit.

Validates 150 active IDs and every source environment through 19 complete
consecutive Stacks sections (including one zero-active section). Does NOT
certify mathematical correctness or theorem-proof equivalence.
"""
from __future__ import annotations
import json,re
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as hp
from scripts.active_candidate_pool import IDS
from scripts.stacks_context_recon import REV

ROOT=Path("harvest/section_walk_scale150_2026-10-28")
READY="standalone_draft_ready_for_validation"
HOLD="context_resolution_pending"
FORMAL={"lemma","proposition","theorem","corollary"}

def main():
    meta=json.loads((ROOT/"MANIFEST.json").read_text())
    draftsmeta=json.loads((ROOT/"DRAFT_MANIFEST.json").read_text())
    scope=json.loads((ROOT/"SCOPES_REVIEWED.json").read_text())
    defs=hp.read_jsonl(ROOT/"SHARED_CONTEXT_EXCERPTS.jsonl")
    all_active=hp.load_rows(IDS,"candidate_id")
    assert len(all_active)==9675
    assert meta["source_revision"]==draftsmeta["source_revision"]==scope["source_revision"]==REV
    assert meta["chapter"]==draftsmeta["file"]=="algebra.tex"
    assert meta["sections"]==draftsmeta["consecutive_complete_sections"]==19
    assert meta["active_candidate_count"]==draftsmeta["distinct_active_candidates_with_drafts"]==150
    assert meta["first_line"]==4284 and meta["last_line"]==10036
    assert meta["consecutive_full_sections"]
    assert len(scope["prose_scope_leads_reviewed"])==2
    assert {x["source_line"] for x in scope["prose_scope_leads_reviewed"]}=={5143,9518}
    assert all(not x["persistent_hypotheses_added"] for x in scope["prose_scope_leads_reviewed"])
    assert len(scope["relevant_source_labels"])==14
    definitions=[q for q in defs if q["kind"]=="definition"]
    assert len(definitions)==14,len(definitions)
    # A definition is a term reference, not a global theorem premise.
    assert all(q["available_as_definition_not_assumption"] for q in definitions)
    assert len({q["label"] for q in definitions})==len(definitions)
    assert all(not q["applies_to_previous_candidates"] for q in definitions)

    allids=set()
    counts=Counter()
    logical=Counter()
    source_events=Counter()
    errors=[]
    cursor=4284
    source_environment_count=0
    extra_source_formal_environments=0
    all_refs=0
    checkpoints=[]
    bysection=[]
    for s in meta["section_inventory"]:
        key=s["key"]
        start=s["source_start_line"]
        end=s["source_end_line"]
        assert start==cursor,(cursor,key,start)
        cursor=end+1
        original=hp.load_rows(ROOT/(key+"_packets.jsonl"),"candidate_id")
        overlays=hp.load_rows(ROOT/(key+"_reviews.jsonl"),"candidate_id")
        events=hp.read_jsonl(ROOT/(key+"_events.jsonl"))
        assert len(original)==len(overlays)==s["active_candidate_count"]
        assert set(original)==set(overlays)
        assert set(overlays).issubset(all_active)
        assert not (set(overlays)&allids)
        allids.update(overlays)
        stack=[]
        active_candidate_events=[]
        source_formal_starts=[]
        for e in events:
            source_events[e["kind"]]+=1
            if e["kind"]=="enter_local_environment":
                stack.append((e["environment"],e["line"]))
                source_environment_count+=1
                if e["environment"] in FORMAL:
                    source_formal_starts.append(e["line"])
            elif e["kind"]=="exit_local_environment":
                assert stack and stack[-1][0]==e["environment"],(key,e,stack)
                stack.pop()
            elif e["kind"]=="candidate_location":
                assert stack and stack[-1][0] in FORMAL
                active_candidate_events.append(e["line"])
        assert not stack,(key,stack)
        assert len(active_candidate_events)==len(overlays)
        assert [x["source_statement_line"] for x in sorted(
            original.values(),key=lambda y:y["source_statement_line"]) ]==active_candidate_events
        extra_source_formal_environments+=len(source_formal_starts)-len(active_candidate_events)
        assert len(source_formal_starts)>=len(active_candidate_events)
        assert all(line in source_formal_starts for line in active_candidate_events)
        secstatuses=Counter()
        for ident,r in overlays.items():
            raw=original[ident]
            assert r["source_revision"]==REV
            assert r["source_filename"]=="algebra.tex"
            assert r["source_label"]==raw["source_label"]
            assert r["source_statement_line"]==raw["source_statement_line"]
            assert r["source_url"]==raw["source_url"]
            assert r["section_start_line"]==start
            assert r["section_end_line"]==end
            assert r["source_environment_start_line"]==r["source_statement_line"]
            assert r["source_environment_end_line"]>r["source_environment_start_line"]
            assert start<=r["source_statement_line"]<=end
            assert r["source_environment"] in FORMAL
            assert r["standalone_statement_tex"]
            assert r["original_source_statement_tex"]==raw["statement_tex"]
            assert r["draft_hypotheses"]
            assert r["draft_conclusions"] or r["source_enumerated_clauses"]
            assert not r["proofs_inspected"]
            assert not r["pass3_eligible"]
            assert not r["published"]
            assert not r["final_standalone_source_equivalence_approved"]
            assert r["source_pass1_pass2_unchanged"]
            assert not r["source_lemma_local_hypotheses_persist_after_end"]
            assert not r["applicable_named_definitions_are_hypotheses"]
            assert r["unconditional_section_hypotheses"]==[]
            assert r["status"] in (READY,HOLD)
            if r["status"]==READY:
                assert not r["context_resolution_needed"],r["source_label"]
                assert r"\ref{" not in r["standalone_statement_tex"],r["source_label"]
                assert all(r"\ref{" not in fragment for fragment in
                           r["draft_hypotheses"]+r["draft_conclusions"]+
                           r["additional_conclusions"]),r["source_label"]
            else:
                assert r["context_resolution_needed"]
            if r["source_enumeration_logical_form"]=="equivalent_conditions":
                assert len(r["draft_conclusions"])>=len(r["source_enumerated_clauses"]),r["source_label"]
                assert not set(r["draft_hypotheses"]) & set(r["source_enumerated_clauses"]),r["source_label"]
            if r["source_enumeration_logical_form"]=="existential_witness_properties":
                assert r["draft_conclusions"]
                assert "simultaneously" in " ".join(r["draft_conclusions"]),r["source_label"]
            assert set(r["applicable_named_definition_ids"])=={
                d["label"] for d in definitions
                if d["source_start_line"]<=r["source_statement_line"]
            }
            # Global commutative rings do not override an explicitly
            # noncommutative theorem object.
            if r["source_label"]=="lemma-lift-idempotents-noncommutative":
                assert "possibly noncommutative" in r["standalone_statement_tex"]
            if r["source_label"]=="lemma-colon":
                assert "J" in str(r["draft_hypotheses"])
            if r["source_label"]=="lemma-minimal-prime-reduced-ring":
                assert any("nilpotent" in x for x in r["draft_conclusions"])
                assert not any("nilpotent" in x for x in r["draft_hypotheses"])
            if r["source_label"]=="proposition-oka":
                assert "maximal" in r["standalone_statement_tex"]
                assert "Oka family" not in r["standalone_statement_tex"]
            all_refs+=len(r["source_refs"])
            counts[r["status"]]+=1
            logical["source_multi_part" if r["source_has_multi_part_form"] else
                    "single_statement"]+=1
            secstatuses[r["status"]]+=1
        # Continuity of accumulated named terms, but NO inherited
        # lemma-specific assumptions. The next section can reference these
        # already encountered definitions without rereading them.
        available_at_end=[
            {"label":q["label"],"source_line":q["source_start_line"],
             "source_url":q["source_url"],"role":"term_definition_only"}
            for q in definitions if q["source_start_line"]<=end]
        if s["key"]=="s04":
            assert len(overlays)==0  # Empty section not skipped
        if s["key"]=="s05":
            assert any(d["label"]=="definition-oka-family" for d in available_at_end)
        if s["key"]=="s13":
            assert any(d["label"]=="definition-integral-closure" for d in available_at_end)
        if s["key"]=="s14":
            assert {d["label"] for d in available_at_end}.issuperset({
                "definition-domain-normal","definition-ring-normal"})
            assert all(r["source_statement_line"]>=8205 or
                       "definition-ring-normal" not in r["applicable_named_definition_ids"]
                       for r in overlays.values())
        if s["key"]=="s18":
            assert any(d["label"]=="definition-going-up-down" for d in available_at_end)
        checkpoints.append({
            "schema":"maththm.consecutive-section-checkpoint.v1",
            "source_revision":REV,
            "section_key":key,
            "source_file":"algebra.tex",
            "section_title":s["section_title"],
            "section_start_line":start,
            "section_end_line":end,
            "next_source_line":end+1,
            "complete_section_processed":True,
            "active_candidate_ids_in_this_section":[x["candidate_id"] for x in sorted(
                overlays.values(),key=lambda r:r["source_statement_line"])],
            "active_candidates_completed":len(overlays),
            "cumulative_completed_candidate_ids_count":len(allids),
            "source_proof_bodies_unread":True,
            "active_temporary_lemma_hypotheses":[],
            "section_ambient_hypotheses":[],
            "available_named_source_definitions":available_at_end,
            "source_scopes_reviewed":[x["source_line"] for x in
                                     scope["prose_scope_leads_reviewed"] if x["source_line"]<=end],
            "complete_section_pass1_pass2_unchanged":True,
            "review_status_counts":dict(secstatuses),
        })
        bysection.append({
            "key":key,"title":s["section_title"],"count":len(overlays),
            "source_range":[start,end],
            "draft_status_counts":dict(secstatuses),
            "source_formal_environments":len(source_formal_starts),
            "source_reference_uses":sum(len(x["source_refs"]) for x in overlays.values()),
            "complete_without_cut":True,
        })
    assert cursor==10037
    assert len(allids)==150
    assert len(checkpoints)==19
    assert sum(x["count"] for x in bysection)==150
    assert sum(x["source_range"][1]-x["source_range"][0]+1 for x in bysection)==5753
    assert counts[READY]+counts[HOLD]==150
    assert sum(source_events[k] for k in ("enter_local_environment",))==sum(
        source_events[k] for k in ("exit_local_environment",))==189
    assert source_events["proof_skipped"]==157
    assert source_events["candidate_location"]==150
    assert set(x["source_line"] for x in scope["prose_scope_leads_reviewed"])=={
        5143,9518}
    hp.atomic_text(ROOT/"SECTION_CHECKPOINTS.jsonl",
        "".join(json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n" for x in checkpoints))
    report={
        "schema":"maththm.consecutive-150-section-walk-validation.v1",
        "source_revision":REV,
        "chapter":"algebra.tex",
        "source_range":[4284,10036],
        "source_lines_traversed":5753,
        "complete_consecutive_sections":19,
        "zero_candidate_sections_also_processed":1,
        "active_candidates_with_saved_draft_overlay":150,
        "draft_status_counts":dict(sorted(counts.items())),
        "source_environment_frames_entered_and_closed":source_environment_count,
        "active_candidate_local_frames_closed":150,
        "other_formal_statement_frames_traversed_not_promoted":extra_source_formal_environments,
        "source_proof_environments_skipped_without_reading_bodies":157,
        "cross_section_named_term_definitions_tracked":14,
        "nonhypothesis_prose_leads_adjudicated":2,
        "complete_section_checkpoints":19,
        "source_reference_uses":all_refs,
        "statement_logical_shapes":dict(sorted(logical.items())),
        "equivalence_clause_scope_crosschecks_applied":True,
        "standalone_ready_hypotheses_and_conclusions_have_no_source_ref_placeholders":True,
        "joint_existential_witness_claims_kept_grouped":True,
        "all_hypotheses_scoped_without_leakage":True,
        "all_candidates_final_source_equivalence_validated":False,
        "proofs_reviewed":0,
        "pass3_eligible":0,
        "original_pass1_pass2_and_active_pool_unchanged":True,
        "published_corpus_unchanged":True,
        "per_section":bysection,
        "limits":[
          "Editorial draft-ready is a triage status; it is not mathematical source equivalence approval.",
          "Preserving a source-complete statement is not the same as expanding all technical definitions inline; encountered definitions are attached by label and provenance.",
          "The source-order event scan does not inspect proof bodies and cannot validate theorem truth.",
          "No measured wall-clock benchmark or maximum sustainable batch size has been established."
        ],
        "suggested_next_batch":"Increase only after checking quality and effort of current 150-candidate drafts; keep whole consecutive sections and independent final math gate."
    }
    hp.atomic_text(ROOT/"VALIDATION.json",json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in (
        "complete_consecutive_sections","active_candidates_with_saved_draft_overlay",
        "draft_status_counts","source_environment_frames_entered_and_closed",
        "other_formal_statement_frames_traversed_not_promoted",
        "cross_section_named_term_definitions_tracked")}))
    return report
if __name__=="__main__":main()

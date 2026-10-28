#!/usr/bin/env python3
"""Validate scoped Situation inheritance and lemma-local hypothesis expiration.

No source proofs, semantic proof claims, publication or candidate promotion.
"""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.stacks_context_recon import REV

ROOT=Path("harvest")
PREFIX="SECTION_WALK_PILOT_LIMITS"
EVENTS=ROOT/(PREFIX+"_EVENTS_2026-10-28.jsonl")
PACKETS=ROOT/(PREFIX+"_PACKETS_2026-10-28.jsonl")
REVIEWS=ROOT/(PREFIX+"_STANDALONE_REVIEWS_2026-10-28.jsonl")
CONTEXT=ROOT/(PREFIX+"_SHARED_CONTEXT_2026-10-28.json")
CHECKPOINTS=ROOT/(PREFIX+"_CONTEXT_CHECKPOINTS_2026-10-28.jsonl")
MANIFEST=ROOT/(PREFIX+"_VALIDATION_2026-10-28.json")

def main():
    source=p.load_rows(PACKETS,"candidate_id")
    drafts=p.load_rows(REVIEWS,"candidate_id")
    scope=json.loads(CONTEXT.read_text(encoding="utf-8"))
    events=p.read_jsonl(EVENTS)
    assert len(source)==len(drafts)==15
    assert scope["source_revision"]==REV
    assert scope["scope_class"]=="section_ambient_situation_with_explicit_references"
    assert len(scope["hypotheses"])==6
    assert scope["declaring_sentence_line"]==1733
    assert scope["named_situation_source_line"]==1738
    assert scope["scope_end_line"]==2127
    assert not scope["applies_beyond_this_section"]
    assert not scope["automatic_scope_propagation"]
    assert any(e["kind"]=="potential_durable_scope_change" and
               e["line"]==scope["declaring_sentence_line"] for e in events)
    stack=[]
    situation_seen=False
    situation_live=False
    candidate_rows=[]
    local_types=Counter()
    entered=Counter()
    exited=Counter()
    seen=set()
    for event in events:
        k=event["kind"]
        if k=="enter_local_environment":
            stack.append((event["environment"],event["line"]))
            entered[event["environment"]]+=1
            if event["environment"]=="situation":
                assert event["line"]==scope["named_situation_source_line"]
                situation_seen=True
        elif k=="exit_local_environment":
            assert stack and stack[-1][0]==event["environment"],(stack,event)
            env,line=stack.pop()
            exited[env]+=1
            if env=="situation":
                assert situation_seen and line==1738
                # The ambient content is now established *only because*
                # the section says it will work in this Situation, and all
                # theorem statements explicitly reference it.
                situation_live=True
        elif k=="candidate_location":
            assert situation_live
            assert len(stack)==1 and stack[-1][0]=="lemma"
            items=[r for r in drafts.values() if r["source_statement_line"]==event["line"]]
            assert len(items)==1
            row=items[0]
            ident=row["candidate_id"]
            assert ident not in seen
            seen.add(ident)
            raw=source[ident]
            text=raw["statement_tex"]
            assert "situation-descent-property" in text
            assert row["source_label"]==raw["source_label"]
            assert row["source_revision"]==REV
            assert row["effective_section_context_ids"]==[scope["context_id"]]
            assert row["resolved_shared_context_id"]==scope["context_id"]
            assert row["explicit_hypotheses"][:len(scope["hypotheses"])]==scope["hypotheses"]
            assert row["standalone_statement_latex"].startswith(r"Let \((S_i)")
            assert r"\ref{" not in row["standalone_statement_latex"]
            assert row["conclusion_claims"]
            assert row["lemma_local_hypotheses_expire_at_lemma_end"]
            assert not row["newly_inherited_lemma_local_conditions"]
            assert row["pass3_eligible"] is False
            assert row["final_standalone_approved"] is False
            assert row["source_proof_screened"] is False
            assert row["original_pass2_unchanged"] is True
            cond="none"
            if any("f0 locally of finite presentation" in s for s in row["lemma_local_hypotheses"]):
                cond="locally_of_finite_presentation"
                assert "locally of finite presentation" in text
            elif any("f0 locally of finite type" in s for s in row["lemma_local_hypotheses"]):
                cond="locally_of_finite_type"
                assert "locally of finite type" in text
            else:
                # The key non-leakage check: local f0 finite-type
                # prerequisites from earlier lemmas do not survive.
                assert "locally of finite type" not in text
                assert "locally of finite presentation" not in text
            local_types[cond]+=1
            candidate_rows.append({
                "source_line":event["line"],
                "candidate_id":ident,
                "statement_label":row["source_label"],
                "active_scoped_situation_context_id":scope["context_id"],
                "ambient_hypotheses":scope["hypotheses"],
                "lemma_local_hypotheses":row["lemma_local_hypotheses"],
                "local_f0_finiteness_guard":cond,
                "lemma_environment_scoped":True,
                "source_revision":REV,
                "source_url":row["source_url"],
                "unresolved_scope_changes":[],
                "theorem_proof_unread":True,
            })
    assert not stack and situation_live
    assert seen==set(drafts)
    assert entered["situation"]==exited["situation"]==1
    assert entered["lemma"]==exited["lemma"]==15
    assert local_types=={"none":2,"locally_of_finite_type":5,
                         "locally_of_finite_presentation":8}, local_types
    assert all(x["source_line"]>=scope["scope_start_line"] for x in candidate_rows)

    # Save a checkpoint after each individual lemma, at which its local
    # variables and finiteness assumptions have been popped. The one
    # explicitly inherited Situation remains in scope until section end.
    checkpoints=[]
    for i,item in enumerate(candidate_rows):
        checkpoints.append({
            "schema":"maththm.section-walk-context-checkpoint.v1",
            "section_id":"limits:section-descent-of-properties",
            "after_candidate_id":item["candidate_id"],
            "after_candidate_source_start_line":item["source_line"],
            "completed_candidates_in_section":[r["candidate_id"] for r in candidate_rows[:i+1]],
            "current_standing_context_ids":[scope["context_id"]],
            "standing_hypotheses":scope["hypotheses"],
            "lemma_local_context_at_checkpoint":[],
            "last_lemma_specific_f0_condition_popped":item["local_f0_finiteness_guard"],
            "available_named_references":["situation-descent-property"],
            "valid_until_section_end_line":2127,
            "must_expire_when_leaving_section":True,
            "no_context_assumed_at_start_of_next_chapter":True,
            "source_revision":REV,
        })
    p.atomic_text(CHECKPOINTS,
        "".join(json.dumps(q,ensure_ascii=False,sort_keys=True)+"\n" for q in checkpoints))
    result={
        "schema":"maththm.section-walk-limits-validation.v1",
        "source_revision":REV,
        "section":"limits.tex:1729-2127",
        "source_lines":399,
        "candidate_count":15,
        "standalone_drafts":15,
        "one_explicit_section_wide_named_situation_reviewed":True,
        "scope_reference_reuse_opportunities":14,
        "local_lemma_scopes_popped":15,
        "local_condition_by_category":dict(sorted(local_types.items())),
        "checkpoint_count":15,
        "durable_scope_rules":1,
        "no_local_finiteness_leak":True,
        "source_reference_resolution_per_candidate":15,
        "all_pass3_eligible":False,
        "proofs_reviewed":0,
        "mathematical_truth_checked":False,
        "drafts_require_final_source_equivalence_validation":True,
        "original_source_pass2_modified":False,
        "persistent_section_context_must_expire_at_line":2127,
        "note":"Persistent Situation justified by explicit section introduction and per-lemma citations; none of the lemma-local finiteness requirements persists to later lemmas."
    }
    p.atomic_text(MANIFEST,json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
    return result

if __name__=="__main__":main()

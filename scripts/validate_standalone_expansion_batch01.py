#!/usr/bin/env python3
"""Audit the first standalone-reconstruction batch against original Stacks intake.

Metadata/structure checks only. They do not verify mathematics or proofs.
No original Pass 1, Pass 2, consolidated intake or public records are changed.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import json
import re
from scripts import harvest_pipeline as p
from scripts.active_candidate_pool import BATCHES,IDS
from scripts.stacks_context_recon import REV

BATCH=Path("harvest/standalone_candidate_expansion_batch01_2026-10-28.jsonl")
MANIFEST=Path("harvest/standalone_candidate_expansion_batch01_2026-10-28_manifest.json")
PROVISIONAL_GROUPS={26,38,50,55,60,84,92,96}

def validate():
    batch=p.load_rows(BATCH,"candidate_id")
    ids=p.load_rows(IDS,"candidate_id")
    assert len(batch)==13, len(batch)
    assert len(ids)==9675, len(ids)
    assert set(batch).issubset(ids)
    p1={}
    p2={}
    for name in BATCHES:
        folder=Path("harvest/batches")/name
        one=p.load_rows(folder/"pass1.jsonl","candidate_id")
        two=p.load_rows(folder/"pass2.jsonl","candidate_id")
        p1.update(one)
        p2.update(two)
    counts=Counter()
    groups=set()
    with_variants=0
    blocked_terms=Counter()
    for ident,row in batch.items():
        assert row["schema"]=="maththm.standalone-expansion-review.v1"
        assert row["source_revision"]==REV==p1[ident]["source"]["revision"]
        assert row["source_filename"]==p1[ident]["source"]["filename"]
        assert row["source_statement_line"]==p1[ident]["source"]["statement_line"]
        assert row["pass3_eligible"] is False
        assert row["published"] is False
        assert row["proof_screened"] is False
        assert row["original_pass1_pass2_unchanged"] is True
        assert row["mathematical_standalone_equivalence_approved"] is row["standalone_source_context_validated"]
        assert row["standalone_source_context_validated"] in (True,False)
        assert row["source_merge_final_approved"] is False
        assert row["hypotheses"] and row["conclusions"]
        assert row["standalone_statement_latex"].strip()
        assert r"\ref{" not in row["standalone_statement_latex"]
        assert not re.search(r"\b(?:Situation|Definition)\s+\\ref",row["standalone_statement_latex"])
        assert row["source_candidate_ids"] and ident in row["source_candidate_ids"]
        assert set(x["candidate_id"] for x in row["original_source_references"])==set(row["source_candidate_ids"])
        assert all(x["source_url"].startswith("https://github.com/stacks/stacks-project/blob/"+REV+"/")
                   for x in row["original_source_references"])
        counts[row["status"]]+=1
        if row["merge_group"] is not None:
            assert row["merge_group"] in PROVISIONAL_GROUPS
            assert len(row["source_candidate_ids"])==2
            groups.add(row["merge_group"])
            with_variants+=1
        else:
            assert len(row["source_candidate_ids"])==1
        if row["status"]=="standalone_source_context_validated":
            assert row["standalone_source_context_validated"]
            assert not row["unresolved_source_specific_context"]
            assert row["standalone_validation_basis"]
            assert row["standalone_validation_source_positions"]
        elif row["status"]=="standalone_draft_ready_for_validation":
            assert not row["unresolved_source_specific_context"]
            assert not row["standalone_source_context_validated"]
        elif row["status"]=="context_resolution_pending":
            assert row["unresolved_source_specific_context"]
            blocked_terms.update(row["terminology_to_check"])
        else:
            raise ValueError(f"Unrecognized status {row['status']}")
    assert groups==PROVISIONAL_GROUPS
    assert counts=={"standalone_source_context_validated":5,
                    "standalone_draft_ready_for_validation":1,
                    "context_resolution_pending":7}
    result={
        "schema":"maththm.standalone-expansion-batch01-manifest.v1",
        "source_revision":REV,
        "reviewed_candidates":len(batch),
        "status_counts":dict(sorted(counts.items())),
        "provisional_source_merge_groups_included":sorted(groups),
        "provisional_source_merge_groups_finalized":0,
        "original_source_occurrences_preserved":len(batch)+with_variants,
        "open_context_issues":sum(len(r["unresolved_source_specific_context"]) for r in batch.values()),
        "open_terminology_leads":dict(sorted(blocked_terms.items())),
        "pass3_eligible":0,
        "source_pass1_pass2_mutated":False,
        "theorem_proofs_screened":0,
        "source_mathematical_equivalence_certified":counts["standalone_source_context_validated"],
        "source_context_validated_without_proof_screening":True,
        "canonical_or_published_records_edited":False,
        "next_step":"One draft still needs standalone terminology validation; seven candidates need focused context resolution. Five have passed standalone source-context checks (not proof checks). Recompare provisional merged aliases before Pass 3.",
    }
    p.atomic_text(MANIFEST,json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
    return result

if __name__=="__main__":
    validate()

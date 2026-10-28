#!/usr/bin/env python3
"""Canonical archive of deferred inherited-context Pass 2 candidates.

The archive is intentionally separate from active bulk/prototype discovery.
It is generated from the current canonical Pass 2 records, preserves exact
candidate IDs and pinned provenance, and can be regenerated on any future
discovery run. Nothing is deleted or reclassified; future review can recover
the full source decision/history via the IDs and the source files.
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.pass2_context_source_probe import BATCHES

DEST=Path("harvest/problem_candidates_inherited_context.jsonl")
MANIFEST=Path("harvest/PROBLEM_CANDIDATES_MANIFEST.json")
SKIP_STATUS={"needs_context"}

def main():
    problems=[]
    counts=Counter()
    all_ids=set()
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        raw=p.load_rows(w/"pass1.jsonl","candidate_id")
        reviewed=p.load_rows(w/"pass2.jsonl","candidate_id")
        assert set(raw)==set(reviewed)
        for ident,r in sorted(reviewed.items()):
            assert ident not in all_ids,ident
            all_ids.add(ident)
            if r["context_status"] not in SKIP_STATUS:continue
            source=raw[ident]["source"]
            problems.append({
                "candidate_id":ident,
                "origin_batch":batch,
                "deferred_phase":"post_prototype_future_discovery",
                "defer_reason":"Inherited mathematical source context is not safely resolved for Pass 2",
                "original_status":r["context_status"],
                "classification":r["result_classification"],
                "source_file":source["filename"],
                "source_revision":source["revision"],
                "source_url":source["source_url"],
                "source_label":source.get("label"),
                "source_statement":r["statement"],
                "detected_references":raw[ident].get("detected_local_references",[]),
                "context_note":r.get("context_note",""),
                "local_context_used":r.get("local_context_used",[]),
                "proofs_read":False,
            })
            counts[batch]+=1
    problems.sort(key=lambda p:p["candidate_id"])
    assert len({r["candidate_id"] for r in problems})==len(problems)
    # Prototype/bulk intake: only canonical resolved entries can be considered,
    # and quarantined context IDs MUST never occur in this active set.
    eligible={ident for batch in BATCHES
        for ident,row in p.load_rows(Path("harvest/batches")/batch/"pass2.jsonl","candidate_id").items()
        if row["context_status"]=="resolved"}
    assert not eligible.intersection(r["candidate_id"] for r in problems)
    p.atomic_text(DEST,"".join(json.dumps(q,sort_keys=True,ensure_ascii=False)+"\n" for q in problems))
    manifest={
        "schema":"maththm.deferred-inherited-context.v1",
        "source_of_truth":"harvest/batches/<batch>/pass2.jsonl plus pass1.jsonl",
        "deferred_file":str(DEST),
        "deferred_status":"needs_context",
        "count":len(problems),
        "by_batch":dict(sorted(counts.items())),
        "active_bulk_prototype_policy":"EXCLUDE all problem_candidates_inherited_context IDs; consider only canonical Pass 2 resolved mathematical_result records, subject to all later validation and publishing gates",
        "future_work":"Revisit after initial bulk discovery and prototype; do not delete or treat as false positives",
        "future_rebuild_command":"python -m scripts.pass2_problem_candidates",
        "quarantined_ids_are_in_active_resolved_set":False,
        "proofs_read":False,
        "published_catalog_untouched":True,
    }
    p.atomic_text(MANIFEST,json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:manifest[k] for k in ("count","by_batch","deferred_file","active_bulk_prototype_policy")},indent=2))
if __name__=="__main__":main()

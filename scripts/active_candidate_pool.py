"""Active prototype population: only completed Pass 2 records, never deferred problems.

Preserve the original Pass 1/2 files as a historical source of truth. A named
active-pool snapshot provides the only authorized candidate IDs for subsequent
Pass 3 screening and promotion of the current Stacks discovery corpus.

This module does not review proofs or mathematics and does not publish data.
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
from scripts import harvest_pipeline as p

BATCHES=("stacks-bulk-2026-10-28",
         "stacks-second-2026-10-28",
         "stacks-remaining-2026-10-28")
IDS=Path("harvest/active_candidate_ids.jsonl")
MANIFEST=Path("harvest/ACTIVE_CANDIDATE_POOL.json")
ARCHIVE=Path("harvest/problem_candidates.jsonl")
SOURCE_STATUS="resolved"

def active_workdir(workdir: Path) -> bool:
    w=Path(workdir).resolve()
    return any(w==(Path("harvest/batches")/b).resolve() for b in BATCHES)

def active_ids_for_workdir(workdir: Path):
    """Return an allowlist for the current discovery batches; None otherwise.

    Other newly harvested workspaces still follow the original Pass 2 resolved
    gate. Existing source batches fail closed if the active snapshot is absent,
    malformed or stale, rather than accidentally reopening deferred candidates.
    """
    if not active_workdir(Path(workdir)):
        return None
    if not IDS.is_file() or not MANIFEST.is_file():
        raise RuntimeError("Active mathThm pool is missing; run python -m scripts.active_candidate_pool")
    batch=Path(workdir).resolve().name
    selected=set()
    for row in p.read_jsonl(IDS):
        if row.get("origin_batch")==batch:
            selected.add(row["candidate_id"])
    if not selected:
        raise RuntimeError(f"No active candidates in {IDS} for {batch}")
    return selected

def main():
    records=[]
    deferred=p.load_rows(ARCHIVE,"candidate_id")
    deferred_ids=set(deferred)
    expected_open={}
    counts=Counter()
    all_ids=set()
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        raw=p.load_rows(w/"pass1.jsonl","candidate_id")
        reviewed=p.load_rows(w/"pass2.jsonl","candidate_id")
        assert set(raw)==set(reviewed)
        for ident,row in sorted(reviewed.items()):
            assert ident not in all_ids,ident
            all_ids.add(ident)
            if row["context_status"]==SOURCE_STATUS and row.get("result_classification")=="mathematical_result":
                assert row["hypotheses"] and row["conclusions"]
                assert ident not in deferred_ids,ident
                records.append({"candidate_id":ident,"origin_batch":batch,
                                "source_revision":raw[ident]["source"]["revision"],
                                "pass2_status":"resolved",
                                "pass3_status":"eligible_unreviewed"})
                counts[batch]+=1
            else:
                expected_open[ident]=row["context_status"]
    assert len(all_ids)==10987
    assert set(expected_open)==deferred_ids, "Deferred archive must cover ALL excluded source records"
    assert all(deferred[k]["original_status"]==expected_open[k] for k in deferred)
    assert len(records)+len(expected_open)==len(all_ids)
    assert not ({r["candidate_id"] for r in records}&deferred_ids)
    records.sort(key=lambda r:r["candidate_id"])
    p.atomic_text(IDS,"".join(json.dumps(x,sort_keys=True)+"\n" for x in records))
    manifest={
        "schema":"maththm.active-discovery-pool.v1",
        "campaign":"2026-10-28-stacks-bulk-prototype",
        "candidate_pool_file":str(IDS),
        "eligible_total":len(records),
        "by_batch":dict(sorted(counts.items())),
        "next_stage":"Pass 3 proof screening, not mathematical verification",
        "eligible_rule":"Only Pass 2 resolved mathematical_result records; apply archive exclusion",
        "excluded_registry":str(ARCHIVE),
        "exclusion_is_nondestructive":True,
        "source_pass1_pass2_immutable":True,
        "proofs_read_by_this_step":False,
        "pass3_screening_started_by_this_step":False,
        "public_catalog_unchanged":True,
        "rebuild_command":"python -m scripts.active_candidate_pool",
    }
    p.atomic_text(MANIFEST,json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"active_candidates":len(records),"by_batch":dict(sorted(counts.items())),
                      "next_stage":"pass3"},sort_keys=True))
if __name__=="__main__":
    main()

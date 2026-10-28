"""Regenerate a grouped future-discovery registry from canonical Pass 2."""
import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from scripts import harvest_pipeline as p
from scripts.pass2_context_source_probe import BATCHES

PATH=Path("harvest/problem_candidates.jsonl")
OLD_PATH=Path("harvest/problem_candidates_inherited_context.jsonl")
MANIFEST=Path("harvest/PROBLEM_CANDIDATES_MANIFEST.json")
GROUPS={"needs_context":"inherited_context","needs_structure":"structural_complexity"}

def structure_type(s):
    if re.search(r"add more here|to do|we should prove",s,re.I):
        return "editorial_placeholder"
    if s.count(r"\begin{enumerate}")>1:
        return "nested_lists"
    if re.search(r"if and only if|the following are equivalent",s,re.I):
        return "equivalence_or_scope"
    if r"\begin{enumerate}" in s:
        return "enumerated_conditions_or_results"
    if r"\xymatrix" in s or r"\begin{diagram}" in s:
        return "diagram_scope"
    if re.search(r"\b(?:if|then|conversely)\b",s,re.I):
        return "conditional_scope"
    return "unconditional_result_or_source_boundary"

def main():
    entries=[]
    by_group=Counter()
    by_batch=Counter()
    by_subtype=Counter()
    by_batch_group=defaultdict(Counter)
    seen=set()
    active=set()
    for batch in BATCHES:
        workdir=Path("harvest/batches")/batch
        raw=p.load_rows(workdir/"pass1.jsonl","candidate_id")
        current=p.load_rows(workdir/"pass2.jsonl","candidate_id")
        assert raw.keys()==current.keys()
        prior=workdir/"pass2_structural_refined_higher_thinking.jsonl"
        old_reasons=p.load_rows(prior,"candidate_id") if prior.exists() else {}
        for ident,decision in sorted(current.items()):
            assert ident not in seen
            seen.add(ident)
            status=decision["context_status"]
            if status=="resolved":
                active.add(ident)
            if status not in GROUPS:
                continue
            group=GROUPS[status]
            subtype=(structure_type(decision["statement"]) if status=="needs_structure"
                     else "inherited_assumptions_notation_or_references")
            source=raw[ident]["source"]
            entries.append({
                "candidate_id":ident,
                "origin_batch":batch,
                "difficulty_group":group,
                "difficulty_subtype":subtype,
                "deferred_until":"later_discovery_after_prototype",
                "original_status":status,
                "result_classification":decision["result_classification"],
                "source_file":source["filename"],
                "source_revision":source["revision"],
                "source_url":source["source_url"],
                "source_label":source.get("label"),
                "source_statement":decision["statement"],
                "detected_references":raw[ident].get("detected_local_references",[]),
                "context_note":decision.get("context_note",""),
                "prior_structural_review_reason":old_reasons.get(ident,{}).get("reason",""),
                "editorial_notes":decision.get("statement_editorial_notes",""),
                "local_context_used":decision.get("local_context_used",[]),
                "proofs_read":False,
            })
            by_group[group]+=1
            by_batch[batch]+=1
            by_subtype[subtype]+=1
            by_batch_group[batch][group]+=1
    entries.sort(key=lambda r:(0 if r["difficulty_group"]=="inherited_context" else 1,r["candidate_id"]))
    assert len(seen)==10987
    assert len({r["candidate_id"] for r in entries})==len(entries)
    assert not active.intersection(r["candidate_id"] for r in entries)
    payload="".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in entries)
    p.atomic_text(PATH,payload)
    p.atomic_text(OLD_PATH,payload)
    assert PATH.read_bytes()==OLD_PATH.read_bytes()
    manifest={
        "schema":"maththm.deferred-problems.v2",
        "source_of_truth":"Each batch's pass2.jsonl and pass1.jsonl",
        "deferred_file":str(PATH),
        "legacy_compatibility_file":str(OLD_PATH),
        "legacy_filename_now_includes_both_groups":True,
        "count":len(entries),
        "by_difficulty":dict(sorted(by_group.items())),
        "by_batch":dict(sorted(by_batch.items())),
        "by_batch_and_difficulty":{k:dict(sorted(v.items())) for k,v in sorted(by_batch_group.items())},
        "by_subtype":dict(sorted(by_subtype.items())),
        "deferred_statuses":GROUPS,
        "active_bulk_prototype_policy":"Exclude every ID in the unified registry. Only canonical resolved mathematical_result records are eligible for further validation.",
        "classification_cases_remaining_separate":True,
        "future_work":"Review both groups after prototyping; neither signifies a rejected theorem",
        "future_rebuild_command":"python -m scripts.pass2_problem_candidates",
        "quarantined_ids_are_in_active_resolved_set":False,
        "proofs_read":False,
        "published_catalog_untouched":True,
    }
    assert sum(by_group.values())==len(entries)==sum(by_batch.values())
    p.atomic_text(MANIFEST,json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:manifest[k] for k in ("count","by_difficulty","by_batch","deferred_file")},indent=2))
if __name__=="__main__":
    main()

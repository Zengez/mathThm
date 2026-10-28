"""Enumerate Phase 2 draft-ready states without automatic mathematical approval."""
import json
from collections import Counter
from pathlib import Path

base=Path("harvest/phase2_semantic_gate_2026-10-28")
reg=json.loads(Path("harvest/SECTION_WALK_COMPLETED_SECTIONS.json").read_text())
reviews=[json.loads(s) for s in (base/"INDIVIDUAL_DECISIONS.jsonl").read_text().splitlines() if s]
decisions={x["candidate_id"]:x for x in reviews}
assert len(decisions)==len(reviews)
found={}
for section in reg["sections"]:
    lines=Path(section["artifacts"]).read_text().splitlines()
    items=[json.loads(s) for s in lines if s.strip()]
    assert len(items)==section["active_candidate_count"]
    for item in items:
        old=item.get("context_review_status") or item.get("review_status") or item.get("status")
        if old!="standalone_draft_ready_for_validation":
            continue
        cid=item.get("candidate_id") or item.get("source_candidate_id")
        assert cid and cid not in found
        decision=decisions.get(cid)
        if decision:
            assert item["source_label"]==decision["source_label"]
        state=("phase3_eligible" if decision and decision["decision"]=="source_equivalence_approved"
               else "reconstruction_revision_required" if decision else "individual_review_pending")
        found[cid]={"candidate_id":cid,"source_label":item["source_label"],
                    "source_file":section["source_file"],
                    "source_line":item.get("source_statement_line",item.get("source_line")),
                    "original_draft":section["artifacts"],
                    "phase2_semantic_state":state,
                    "phase3_eligible":state=="phase3_eligible",
                    "review_note":decision["semantic_review_note"] if decision else None,
                    "proof_screened":False}
assert len(found)==1242,len(found)
assert set(decisions)<=set(found)
states=list(found.values())
states.sort(key=lambda x:(x["source_file"],x["source_line"] or 0))
(base/"ALL_DRAFT_READY_STATES.jsonl").write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in states))
counts=Counter(x["phase2_semantic_state"] for x in states)
assert counts=={"phase3_eligible":68,"reconstruction_revision_required":8,"individual_review_pending":1166},counts
m=json.loads((base/"VALIDATION.json").read_text())
m["all_draft_ready_ids_individually_indexed"]=True
m["counts_reconciled_against_original_section_files"]=dict(counts)
(base/"VALIDATION.json").write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
print("Phase 2 semantic gate reconciled:",dict(counts),flush=True)

#!/usr/bin/env python3
"""Fresh resumable Pass 2 review queues derived ONLY from canonical records.

Do not rely on dated interim queues, which may include candidates subsequently
resolved. This script writes neither the published catalog nor proof decisions.
"""
import json
import re
from collections import Counter
from pathlib import Path
from scripts import harvest_pipeline as p

BATCHES=("stacks-bulk-2026-10-28","stacks-second-2026-10-28","stacks-remaining-2026-10-28")
OPEN={"needs_context":"pass2_current_context_queue.jsonl",
      "needs_structure":"pass2_current_structure_queue.jsonl",
      "needs_classification":"pass2_current_classification_queue.jsonl",
      "not_result":"pass2_current_nonresult_queue.jsonl"}
def main():
    total=Counter()
    batches=[]
    falsepositive=[]
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        raw=p.load_rows(w/"pass1.jsonl","candidate_id")
        decisions=p.load_rows(w/"pass2.jsonl","candidate_id")
        assert set(raw)==set(decisions)
        queues={status:[] for status in OPEN}
        states=Counter()
        for ident,row in sorted(decisions.items()):
            state=row["context_status"]
            states[state]+=1
            if state=="resolved":
                assert row["hypotheses"] and row["conclusions"]
                if row.get("logical_form","").startswith("equivalence"):
                    assert all(side in row["hypotheses"] and side in row["conclusions"]
                               for group in row.get("equivalence_sides",[]) for side in group)
                continue
            assert state in OPEN,state
            source=raw[ident]["source"]
            obj={
              "candidate_id":ident,
              "source_filename":source["filename"],
              "source_revision":source["revision"],
              "source_url":source["source_url"],
              "source_statement":row["statement"],
              "source_entry_type":raw[ident]["entry_type"],
              "original_provenance_label":source.get("label"),
              "detected_references":raw[ident].get("detected_local_references",[]),
              "context_status":state,
              "result_classification":row.get("result_classification","uncertain"),
              "current_review_note":row.get("context_note",""),
              "local_context_used":row.get("local_context_used",[]),
              "next_stage":"Pass 2 textual context/structure review only",
              "proofs_read":False,
            }
            queues[state].append(obj)
            if state=="needs_classification":falsepositive.append(obj)
        for state,filename in OPEN.items():
            p.atomic_text(w/filename,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in queues[state]))
        assert sum(states.values())==len(raw)
        total.update(states)
        batches.append({"batch":batch,"candidates":len(raw),"states":dict(sorted(states.items()))})
    resume={
       "schema":"maththm.pass2-resume.v1",
       "batches":batches,
       "all_candidates":sum(x["candidates"] for x in batches),
       "all_statuses":dict(sorted(total.items())),
       "open_total":sum(v for k,v in total.items() if k!="resolved"),
       "classification_details":falsepositive,
       "canonical_source":"Each batch's pass2.jsonl, not prior review queues",
       "source_revision":"a04446e57ec1fbc252a871afcec7752fb2807b14",
       "mathematical_validity_audited":False,
       "proofs_read":False,"pass3_started":False,
       "published_theorem_corpus_edited":False,
    }
    assert resume["all_candidates"]==10987
    assert resume["all_statuses"].get("resolved")==9383
    p.atomic_text(Path("harvest/PASS2_RESUME_INVENTORY_2026-10-28.json"),
                  json.dumps(resume,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print(json.dumps({k:v for k,v in resume.items() if k!="classification_details"},indent=2))

if __name__=="__main__":main()

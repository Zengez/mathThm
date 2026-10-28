"""Materialize review packets for the 102 surface-matched groups, no mergers."""
import json
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.active_candidate_pool import BATCHES
DUP=Path("harvest/PASS3_PRECHECK_SURFACE_DUPLICATES_2026-10-28.json")
DEST=Path("harvest/DUPLICATE_GROUP_REVIEW_2026-10-28.jsonl")
def main():
    report=json.loads(DUP.read_text())
    pairs=report["groups"]["pass2_statement_exact"]["all_groups"]
    src={};p2={}
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        src.update(p.load_rows(w/"pass1.jsonl","candidate_id"))
        p2.update(p.load_rows(w/"pass2.jsonl","candidate_id"))
    lines=[]
    for i,g in enumerate(pairs,1):
        ids=sorted(g["candidate_ids"])
        records=[]
        for ident in ids:
            r=src[ident];t=p2[ident];s=r["source"]
            records.append({
                "id":ident,"batch":r.get("batch_id"),
                "source_file":s.get("filename"),"source_label":s.get("label"),
                "statement_locator":s.get("statement_locator"),"proof_locator":s.get("proof_locator"),
                "source_url":s.get("source_url"),"proof_url":s.get("proof_url"),
                "entry_type":r.get("entry_type"),
                "source_statement":r.get("statement_tex","")[:1200],
                "structured_statement":t.get("statement","")[:1200],
                "hypotheses":t.get("hypotheses"),"conclusions":t.get("conclusions"),
                "logical_form":t.get("logical_form"),
                "context_note":t.get("context_note"),
                "structured_cases":t.get("structured_cases",[]),
                "source_revision":s.get("revision"),
            })
        same_source=len({x["source_url"] for x in records})==1
        same_proof=len({x["proof_url"] for x in records})==1
        same_sides=len({json.dumps([x["hypotheses"],x["conclusions"]],sort_keys=True) for x in records})==1
        same_raw=len({x["source_statement"] for x in records})==1
        row={"group_number":i,"size":len(ids),
             "same_source_url":same_source,"same_proof_url":same_proof,
             "same_hypothesis_conclusion":same_sides,"same_raw_source_text":same_raw,
             "records":records}
        lines.append(row)
    p.atomic_text(DEST,"".join(json.dumps(q,sort_keys=True,ensure_ascii=False)+"\n" for q in lines))
    print(json.dumps({"groups":len(lines),"single_source":sum(x["same_source_url"] for x in lines),
                      "same_proof":sum(x["same_proof_url"] for x in lines),
                      "same_sides":sum(x["same_hypothesis_conclusion"] for x in lines),
                      "same_raw":sum(x["same_raw_source_text"] for x in lines)},sort_keys=True))
if __name__=="__main__":
    main()

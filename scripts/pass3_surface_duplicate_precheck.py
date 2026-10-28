"""Fast, conservative surface duplicate scan; does not read proofs or change intake."""
import json,re,hashlib
from collections import defaultdict,Counter
from pathlib import Path
from scripts import harvest_pipeline as p
from scripts.active_candidate_pool import BATCHES,IDS,MANIFEST
def norm(s):
    s=re.sub(r"\\label\{[^{}]*\}","",s or "")
    s=re.sub(r"\\(?:begin|end)\{[^{}]*\}","",s)
    s=re.sub(r"\s+","",s).lower()
    return s
def main():
    active=p.load_rows(IDS,"candidate_id")
    groups={k:defaultdict(list) for k in ("source_statement_exact","pass2_statement_exact","split_sides_exact")}
    seen=set()
    for batch in BATCHES:
        w=Path("harvest/batches")/batch
        raw=p.load_rows(w/"pass1.jsonl","candidate_id")
        p2=p.load_rows(w/"pass2.jsonl","candidate_id")
        for ident in sorted(set(raw)&set(p2)&set(active)):
            assert ident not in seen
            seen.add(ident)
            source=raw[ident].get("statement_tex","")
            structured=p2[ident]
            values={
                "source_statement_exact":norm(source),
                "pass2_statement_exact":norm(structured.get("statement","")),
                "split_sides_exact":json.dumps([sorted(norm(x) for x in structured["hypotheses"]),
                    sorted(norm(x) for x in structured["conclusions"])],sort_keys=True),
            }
            for key,val in values.items():
                if val and val not in ("[]","[[], []]"):
                    groups[key][val].append(ident)
    assert seen==set(active)
    out={"schema":"maththm.prototype-surface-duplicate-scan.v1",
         "scope":"active candidate pool only",
         "candidate_count":len(active),
         "method":"lowercase/whitespace-normalized exact matches, plus exact normalized two-side splits; no semantic equivalence detection",
         "groups":{},
         "no_candidate_excluded_or_merged":True,
         "pass3_proofs_read":False}
    for kind,table in groups.items():
        dup=[{"candidate_ids":ids,"count":len(ids)} for ids in table.values() if len(ids)>1]
        dup.sort(key=lambda d:(-d["count"],d["candidate_ids"]))
        out["groups"][kind]={"duplicate_groups":len(dup),
            "candidates_in_groups":sum(x["count"] for x in dup),
            "possible_redundant_entries":sum(x["count"]-1 for x in dup),
            "examples":dup[:25],
            "all_groups":dup}
    dest=Path("harvest/PASS3_PRECHECK_SURFACE_DUPLICATES_2026-10-28.json")
    p.atomic_text(dest,json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print(json.dumps({"candidate_count":len(active),"groups":{k:{z:v[z] for z in ("duplicate_groups","candidates_in_groups","possible_redundant_entries")} for k,v in out["groups"].items()}},sort_keys=True))
if __name__=="__main__":main()

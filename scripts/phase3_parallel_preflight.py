"""One-time, read-only audit of four frozen Stage B-positive Phase 3 queues.

Does NOT infer mathematical approval, read proofs, or change registration.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path("work/phase3-parallel")
REV = "a04446e57ec1fbc252a871afcec7752fb2807b14"
ALLOWED = "source_equivalence_approved_pending_materialization"
HELD = "held_for_correction_or_context"

def blob_sha(content):
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()

def audit(workers):
    report = []
    all_ids = set()
    global_paths = set()
    for worker in workers:
        q = json.loads((ROOT / f"worker-{worker}/PENDING.json").read_text())
        assert q["worker"] == worker and q["source_revision"] == REV
        # The queue may shrink as work finishes. For a complete baseline audit,
        # use the untouched parallel-base commit.
        files = [x for batch in q["pending"] for x in batch["sections"]]
        positive_ids = set()
        held_ids = set()
        source_files = set()
        for section in files:
            name = section["file"]
            assert f"/worker-{worker}/results/" in name
            assert name not in source_files and name not in global_paths, name
            source_files.add(name)
            global_paths.add(name)
            data = Path(name).read_bytes()
            assert blob_sha(data) == section["blob_sha"], name
            rows = [json.loads(line) for line in data.decode().splitlines() if line.strip()]
            for row in rows:
                assert row["source_revision"] == REV
                assert row["section_start_line"] == section["section_start_line"]
                assert row["source_file"] == section["file"].split("/results/")[1].split("/")[0] + ".tex"
                assert row["stage_a_artifact"]
                assert row["source_first_review"] is True and row["proof_reviewed"] is False
                assert row["reviewer"] == f"chatgpt-stage-b-independent-worker-{worker}"
                cid = row["candidate_id"]
                assert cid not in positive_ids and cid not in held_ids and cid not in all_ids, cid
                if row["decision"] == ALLOWED:
                    for f in ("statement", "hypotheses", "conclusions", "logical_form", "original_source_statement_tex", "review_note"):
                        assert row.get(f), (cid, f)
                    positive_ids.add(cid)
                else:
                    assert row["decision"] == HELD and row["hold_reason"], cid
                    held_ids.add(cid)
        assert not positive_ids & held_ids
        all_ids.update(positive_ids | held_ids)
        report.append(dict(worker=worker, section_files=len(files),
                           positive=len(positive_ids), held=len(held_ids),
                           remaining_batches=len(q["pending"])))
        if len(q["pending"]) == q["initial_batch_count"]:
            assert len(positive_ids) == q["expected_positive_ids"], worker
            assert len(files) == q["section_files"], worker
    print(json.dumps(dict(worker_audits=report, distinct_ids=len(all_ids)), indent=2))
    if workers == [1, 2, 3, 4] and all(
        r["remaining_batches"] == json.loads((ROOT / f"worker-{r['worker']}/PENDING.json").read_text())["initial_batch_count"]
        for r in report
    ):
        assert sum(x["positive"] for x in report) == 3866
        assert sum(x["held"] for x in report) == 768
        assert sum(x["section_files"] for x in report) == 1244

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=int, choices=(1, 2, 3, 4))
    args = parser.parse_args()
    audit([args.worker] if args.worker else [1, 2, 3, 4])

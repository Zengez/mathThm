"""Active Stacks population safeguards and legacy local-workspace compatibility."""
import argparse
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import active_candidate_pool as pool
from scripts import harvest_pipeline as pipeline

class ActivePoolTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.old_cwd=os.getcwd()
        os.chdir(temp.name)
        self.addCleanup(os.chdir,self.old_cwd)
        self.batch="demo-stacks"
        self.w=Path("harvest/batches")/self.batch
        self.w.mkdir(parents=True)
        self.src=Path("original.tex")
        self.src.write_text("start\nproof\nis true\nfinishes\n",encoding="utf-8")
        self.a="candidate.stacks.active-demo"
        self.d="candidate.stacks.deferred-demo"
        raw=[]
        structured=[]
        for ident,status in ((self.a,"resolved"),(self.d,"needs_structure")):
            raw.append({
                "candidate_id":ident,
                "proof_end_marker_found":True,
                "source":{
                    "filename":"original.tex","revision":"a"*40,
                    "proof_start_line":2,"proof_end_line":4,
                    "confidence":"high",
                    "proof_url":"https://example.org/original#L2",
                    "proof_locator":"original.tex:2",
                },
            })
            structured.append({
                "candidate_id":ident,
                "context_status":status,
                "result_classification":"mathematical_result",
                "statement":"A demonstrative assertion.",
                "hypotheses":["Given A"],"conclusions":["B"] if status=="resolved" else [],
            })
        self.rawfile=self.w/"pass1.jsonl"
        self.p2file=self.w/"pass2.jsonl"
        pipeline.atomic_text(self.rawfile,"".join(json.dumps(x)+"\n" for x in raw))
        pipeline.atomic_text(self.p2file,"".join(json.dumps(x)+"\n" for x in structured))
        pool.ARCHIVE.parent.mkdir(parents=True,exist_ok=True)
        pipeline.atomic_text(pool.ARCHIVE,json.dumps({
            "candidate_id":self.d,"original_status":"needs_structure"
        })+"\n")
        self.mock=patch.object(pool,"BATCHES",(self.batch,))
        self.mock.start()
        self.addCleanup(self.mock.stop)
        with patch.object(pool,"EXPECTED_SOURCE_COUNT",2):
            pool.main()

    def test_deferred_records_never_enter_active_pass3_packets(self):
        candidates=pipeline.load_rows(pool.IDS,"candidate_id")
        self.assertEqual(set(candidates),{self.a})
        self.assertEqual(pool.active_ids_for_workdir(self.w),{self.a})
        pipeline.pass3_packets(argparse.Namespace(
            workdir=str(self.w),source_root=".",max_proof_chars=250))
        packets=pipeline.load_rows(self.w/"pass3_packets.jsonl","candidate_id")
        self.assertEqual(set(packets),{self.a})
        self.assertFalse(packets[self.a]["excerpt_truncated"])

    def test_deferred_record_cannot_be_manually_entered_as_pass3(self):
        path=Path("decisions.jsonl")
        pipeline.atomic_text(path,json.dumps({
            "candidate_id":self.d,"outcome":"plausible",
            "scan_completed":True,"proof_checked_on":"2026-10-28"
        })+"\n")
        with self.assertRaisesRegex(ValueError,"outside active prototype population"):
            pipeline.apply_pass3(argparse.Namespace(
                workdir=str(self.w),decisions=str(path),replace=False))

    def test_active_checkpoints_do_not_report_deferred_problems(self):
        pipeline.refresh_needs(self.w)
        state=json.loads((self.w/"checkpoint.json").read_text())
        self.assertEqual(state["population_scope"],"prototype_active_only")
        self.assertEqual(state["counts"]["pass1"],1)
        self.assertEqual(state["counts"]["pass2"],1)
        self.assertEqual(state["counts"]["needs_more_investigation"],0)
        self.assertEqual(pipeline.read_jsonl(self.w/"needs_more_investigation.jsonl"),[])

    def test_existing_canonical_data_remains_unchanged(self):
        original=(self.rawfile.read_bytes(),self.p2file.read_bytes())
        pipeline.refresh_needs(self.w)
        self.assertEqual((self.rawfile.read_bytes(),self.p2file.read_bytes()),original)
        self.assertEqual(len(pipeline.read_jsonl(pool.ARCHIVE)),1)

if __name__=="__main__":
    unittest.main()

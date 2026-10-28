"""Offline end-to-end acquisition tests: no network, models or proof research."""
from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

from scripts import harvest_pipeline as pipeline
from scripts import harvest_stacks
from scripts.theorem_schema import validate

STOCK_TEX = r"""
\section{Examples}
\begin{lemma}
\label{lemma-one}
Let $X$ be a compact space. If $f$ is continuous, then $f(X)$ is compact.
\end{lemma}
\begin{proof}
Suppose $V_i$ cover the image. Pull the covering back.
By compactness select a finite subcover. This finishes.
\end{proof}

\begin{proposition}
\label{proposition-two}
Under the assumptions of Lemma \ref{lemma-one}, some result follows.
\end{proposition}
\begin{proof}
This follows from the previous lemma. Done.
\end{proof}

\begin{lemma}
\label{lemma-no-proof}
A question: is every set compact?
\end{lemma}

\begin{exercise}
Prove that one is one.
\end{exercise}
\begin{proof}
Not a theorem to harvest.
\end{proof}
"""
REF="a"*40


class HarvestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/"categories.tex"
        self.source.write_text(STOCK_TEX,encoding="utf-8")
        self.w=self.root/"work"
        harvest_stacks.run(argparse.Namespace(
            source_root=str(self.root),source_ref=REF,files=[str(self.source)],
            batch_id="test-stacks-001",output_dir=str(self.w),
            max_candidates_per_file=20,max_file_bytes=100000))
        self.raw=pipeline.load_rows(self.w/"pass1.jsonl","candidate_id")
        self.by_label={r["source"]["label"]:r for r in self.raw.values()}

    def write_decisions(self,name,entries):
        path=self.root/name
        path.write_text("".join(json.dumps(x)+"\n" for x in entries),encoding="utf-8")
        return path

    def run_pass2(self):
        pipeline.pass2_packets(argparse.Namespace(
            workdir=str(self.w),source_root=str(self.root),
            max_local_references=2,max_context_chars=1000))
        self.one=self.by_label["lemma-one"]["candidate_id"]
        self.two=self.by_label["proposition-two"]["candidate_id"]
        packets=pipeline.load_rows(self.w/"pass2_packets.jsonl","candidate_id")
        self.assertIn("lemma-one",packets[self.two]["local_context_excerpts"])
        self.write_decisions("pass2-decisions.jsonl",[
            {"candidate_id":self.one,"context_status":"resolved",
             "statement":"If $f$ is continuous on compact $X$, then $f(X)$ is compact.",
             "hypotheses":["$X$ compact","$f$ continuous"],
             "conclusions":["$f(X)$ compact"],
             "hypothesis_tags":["compactness","continuity"],"conclusion_tags":["compactness"],
             "area":"Topology","title":"Compact image",
             "context_note":""},
            {"candidate_id":self.two,"context_status":"needs_context",
             "statement":"","hypotheses":[],"conclusions":[],
             "context_note":"Local setup not independently extracted"}])
        pipeline.apply_pass2(argparse.Namespace(
            workdir=str(self.w),decisions=str(self.root/"pass2-decisions.jsonl"),replace=False))

    def test_pass1_is_bounded_proof_marker_only_and_repeatable(self):
        self.assertEqual(len(self.raw),2)
        self.assertEqual(set(self.by_label),{"lemma-one","proposition-two"})
        for row in self.raw.values():
            self.assertTrue(row["proof_end_marker_found"])
            self.assertEqual(row["status"],"raw_candidate_unreviewed")
            self.assertNotIn("proof_text",row)
            self.assertIn("#L",row["source"]["proof_url"])
            proof_line=row["source"]["proof_start_line"]
            self.assertEqual(self.source.read_text().splitlines()[proof_line-1].strip(),r"\begin{proof}")
            self.assertEqual(row["source"]["revision"],REF)
        harvest_stacks.run(argparse.Namespace(
            source_root=str(self.root),source_ref=REF,files=[str(self.source)],
            batch_id="test-stacks-001",output_dir=str(self.w),
            max_candidates_per_file=20,max_file_bytes=100000))
        self.assertEqual(len(pipeline.read_jsonl(self.w/"pass1.jsonl")),2)

    def test_pass2_local_reference_is_shallow_and_questionables_are_separate(self):
        self.run_pass2()
        state=json.loads((self.w/"checkpoint.json").read_text())
        self.assertEqual(state["counts"]["pass2"],2)
        self.assertEqual(state["counts"]["needs_more_investigation"],1)
        needs=pipeline.read_jsonl(self.w/"needs_more_investigation.jsonl")
        self.assertEqual(needs[0]["status"],"needs_context")
        self.assertEqual(needs[0]["candidate_id"],self.two)

    def test_pass3_plausible_promotes_only_accepted_candidate(self):
        self.run_pass2()
        pipeline.pass3_packets(argparse.Namespace(
            workdir=str(self.w),source_root=str(self.root),max_proof_chars=9000))
        packets=pipeline.load_rows(self.w/"pass3_packets.jsonl","candidate_id")
        self.assertEqual(len(packets),1)
        self.assertFalse(packets[self.one]["excerpt_truncated"])
        decisions=self.write_decisions("pass3-decisions.jsonl",[
            {"candidate_id":self.one,"outcome":"plausible","scan_completed":True,
             "reason":"Short read found no evident issue","proof_checked_on":"2026-10-28"}])
        pipeline.apply_pass3(argparse.Namespace(workdir=str(self.w),
            decisions=str(decisions),replace=False))
        catalog={"schema":"maththm.theorems.v1","contract_revision":2,"total":0,"records":[]}
        source=self.root/"accepted.json"
        source.write_text(json.dumps(catalog),encoding="utf-8")
        staged=self.root/"staged.json"
        args=argparse.Namespace(workdir=str(self.w),catalog=str(source),
                                output=str(staged),in_place=False)
        pipeline.promote(args)
        result=json.loads(staged.read_text(encoding="utf-8"))
        self.assertEqual(validate(result)["records"],1)
        self.assertEqual(result["records"][0]["proof_plausibility"]["status"],"plausible")
        self.assertEqual(result["records"][0]["mathematical_audit"]["status"],"not_audited")
        self.assertFalse((self.w/"provisional.jsonl").exists())
        self.assertEqual(len(pipeline.read_jsonl(self.w/"needs_more_investigation.jsonl")),1)
        pipeline.promote(args)
        self.assertEqual(len(json.loads(staged.read_text())["records"]),1)

    def test_truncated_packet_cannot_claim_plausible_without_explicit_full_scan(self):
        self.run_pass2()
        pipeline.pass3_packets(argparse.Namespace(
            workdir=str(self.w),source_root=str(self.root),max_proof_chars=10))
        d=self.write_decisions("pass3-decisions.jsonl",[
            {"candidate_id":self.one,"outcome":"plausible","scan_completed":True,
             "reason":"","proof_checked_on":"2026-10-28"}])
        with self.assertRaisesRegex(ValueError,"truncated proof packet"):
            pipeline.apply_pass3(argparse.Namespace(
                workdir=str(self.w),decisions=str(d),replace=False))
        self.assertFalse((self.w/"pass3.jsonl").exists())

    def test_questionable_and_rejected_require_explicit_reason(self):
        self.run_pass2()
        decisions=self.write_decisions("pass3-decisions.jsonl",[
            {"candidate_id":self.one,"outcome":"questionable","scan_completed":False,
             "reason":"Requires an unexamined reference", "proof_checked_on":"2026-10-28"}])
        pipeline.apply_pass3(argparse.Namespace(
            workdir=str(self.w),decisions=str(decisions),replace=False))
        needs=pipeline.load_rows(self.w/"needs_more_investigation.jsonl","candidate_id")
        self.assertEqual(set(needs),{self.one,self.two})
        self.assertEqual(needs[self.one]["status"],"questionable")
        decisions=self.write_decisions("other.jsonl",[
            {"candidate_id":self.one,"outcome":"rejected","scan_completed":True,
             "reason":"Specific step assumes the desired conclusion","proof_checked_on":"2026-10-28"}])
        pipeline.apply_pass3(argparse.Namespace(
            workdir=str(self.w),decisions=str(decisions),replace=True))
        needs=pipeline.load_rows(self.w/"needs_more_investigation.jsonl","candidate_id")
        self.assertEqual(needs[self.one]["status"],"rejected")
        self.assertIn("Specific step",needs[self.one]["reason"])

    def test_cannot_silently_overwrite_accepted_catalog(self):
        self.run_pass2()
        blank={"schema":"maththm.theorems.v1","contract_revision":2,"records":[],"total":0}
        file=self.root/"accepted.json"
        file.write_text(json.dumps(blank))
        with self.assertRaisesRegex(ValueError,"requires explicit --in-place"):
            pipeline.promote(argparse.Namespace(
                workdir=str(self.w),catalog=str(file),output=str(file),in_place=False))


if __name__=="__main__":
    unittest.main()

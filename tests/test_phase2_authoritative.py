"""Mathematical approval provenance and actual downstream formulation safeguards."""
import argparse
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import phase2_authoritative as authority
from scripts import harvest_pipeline as pipeline


class AuthoritativeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.draft = self.root/"draft.jsonl"
        self.draft.write_text("Historical immutable reconstruction\n")
        self.row = dict(candidate_id="candidate.stacks.demo", source_revision=authority.REV,
                        source_label="lemma-demo", source_file="algebra.tex", source_line=1,
                        statement="If A, then B.", hypotheses=["A"], conclusions=["B"],
                        logical_form="single_implication", structured_cases=[], equivalence_sides=[],
                        semantic_review_note="Independent source-first comparison completed.",
                        original_source_statement_tex="Original source statement.",
                        source_statement_sha256=hashlib.sha256(b"Original source statement.").hexdigest(),
                        original_draft=str(self.draft), original_draft_sha256=hashlib.sha256(self.draft.read_bytes()).hexdigest(),
                        phase2_validated=True, phase3_eligible=True, duplicate_review_status="clear")
        self.row["approved_content_sha256"] = authority.content_digest(self.row)
        self.overlayfile = self.root/"approved.jsonl"
        self.overlayfile.write_text(json.dumps(self.row)+"\n")
        self.registry = self.root/"registry.json"
        self.registry.write_text(json.dumps(dict(source_revision=authority.REV, overlay_files=[str(self.overlayfile)])))
        self.old = dict(candidate_id=self.row["candidate_id"], context_status="resolved",
                        statement="Old incorrect draft", hypotheses=["Wrong premise"], conclusions=["Wrong result"],
                        logical_form="wrong", structured_cases=[{}], equivalence_sides=["wrong"])
        self.raw = dict(candidate_id=self.row["candidate_id"], proof_end_marker_found=True,
                        statement_tex=self.row["original_source_statement_tex"],
                        source=dict(revision=authority.REV, filename="algebra.tex", label="lemma-demo", statement_line=1,
                                    proof_start_line=2, proof_end_line=3, confidence="high",
                                    proof_url="https://example.org/proof", proof_locator="fixture"))

    def test_only_explicit_registered_approved_formulations_load(self):
        (self.root/"unregistered.jsonl").write_text("not even valid JSON")
        loaded = authority.load_approved(self.registry)
        self.assertEqual(set(loaded), {self.row["candidate_id"]})
        self.assertEqual(loaded[self.row["candidate_id"]]["statement"], "If A, then B.")

    def test_missing_registry_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "blocked"):
            authority.load_approved(self.root/"missing.json")

    def test_missing_overlay_and_conflicting_duplicates_fail_closed(self):
        self.overlayfile.unlink()
        with self.assertRaisesRegex(RuntimeError, "missing"):
            authority.load_approved(self.registry)
        self.overlayfile.write_text((json.dumps(self.row)+"\n")*2)
        with self.assertRaisesRegex(ValueError, "Duplicate authoritative"):
            authority.load_approved(self.registry)

    def test_unapproved_duplicate_pending_and_wrong_revision_rejected(self):
        for field, value in (("phase2_validated", False), ("phase3_eligible", False),
                             ("duplicate_review_status", "pending"), ("source_revision", "b"*40)):
            r = dict(self.row, **{field:value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                authority.validate_overlay(r)

    def test_edits_to_approved_formula_or_original_draft_invalidate_digest(self):
        with self.assertRaisesRegex(ValueError, "formulation digest"):
            authority.validate_overlay(dict(self.row, statement="If B, then A."))
        self.draft.write_text("Changed after review")
        with self.assertRaisesRegex(ValueError, "provenance"):
            authority.validate_overlay(self.row)

    def test_raw_source_mismatch_cannot_consume_approval(self):
        for field,value in (("statement_line",2),("label","wrong"),("filename","wrong.tex"),("revision","c"*40)):
            raw=copy.deepcopy(self.raw)
            raw["source"][field]=value
            with self.subTest(field=field), self.assertRaises(ValueError):
                authority.apply_overlay(self.old,self.row,raw=raw)
        with self.assertRaisesRegex(ValueError,"original source statement"):
            authority.apply_overlay(self.old,self.row,raw=dict(self.raw,statement_tex="Other theorem"))

    def test_actual_packet_consumes_authoritative_statement_split_and_cases(self):
        w = self.root/"work"
        w.mkdir()
        for filename, row in (("pass1.jsonl", self.raw), ("pass2.jsonl", self.old)):
            (w/filename).write_text(json.dumps(row)+"\n")
        # Synthetic proof markers only; this does not read or screen corpus proofs.
        (self.root/"algebra.tex").write_text("statement\nfixture proof marker\nend marker\n")
        old_bytes = (w/"pass2.jsonl").read_bytes()
        with patch.object(pipeline, "discovery_active_ids", return_value={self.row["candidate_id"]}), \
             patch.object(pipeline, "phase2_approved_overlays", return_value={self.row["candidate_id"]:self.row}), \
             patch("scripts.candidate_consolidation.load_merged_by_canonical", return_value={}):
            pipeline.pass3_packets(argparse.Namespace(workdir=str(w), source_root=str(self.root), max_proof_chars=500))
        packet = json.loads((w/"pass3_packets.jsonl").read_text())
        for field in ("statement", "hypotheses", "conclusions", "logical_form", "structured_cases", "equivalence_sides"):
            self.assertEqual(packet[field], self.row[field])
        self.assertEqual(packet["phase2_approved_content_sha256"], self.row["approved_content_sha256"])
        self.assertEqual((w/"pass2.jsonl").read_bytes(), old_bytes)

    def test_unapproved_candidate_does_not_produce_packet(self):
        w = self.root/"work"
        w.mkdir()
        (w/"pass1.jsonl").write_text(json.dumps(self.raw)+"\n")
        (w/"pass2.jsonl").write_text(json.dumps(self.old)+"\n")
        with patch.object(pipeline, "discovery_active_ids", return_value={self.row["candidate_id"]}), \
             patch.object(pipeline, "phase2_approved_overlays", return_value={}), \
             patch("scripts.candidate_consolidation.load_merged_by_canonical", return_value={}):
            pipeline.pass3_packets(argparse.Namespace(workdir=str(w), source_root=str(self.root), max_proof_chars=500))
        self.assertEqual((w/"pass3_packets.jsonl").read_text(), "")

    def test_stale_packet_cannot_receive_proof_decision(self):
        w = self.root/"work"
        w.mkdir()
        for filename,row in (("pass1.jsonl",self.raw),("pass2.jsonl",self.old),
                             ("pass3_packets.jsonl",dict(candidate_id=self.row["candidate_id"],phase2_approved_content_sha256="old"))):
            (w/filename).write_text(json.dumps(row)+"\n")
        decisions = self.root/"decisions.jsonl"
        decisions.write_text(json.dumps(dict(candidate_id=self.row["candidate_id"],outcome="plausible"))+"\n")
        with patch.object(pipeline, "discovery_active_ids", return_value={self.row["candidate_id"]}), \
             patch.object(pipeline, "phase2_approved_overlays", return_value={self.row["candidate_id"]:self.row}):
            with self.assertRaisesRegex(ValueError,"regenerate packet"):
                pipeline.apply_pass3(argparse.Namespace(workdir=str(w),decisions=str(decisions),replace=False))
        self.assertFalse((w/"pass3.jsonl").exists())


class HistoricalCorrectionTests(unittest.TestCase):
    def test_existing_68_approvals_and_four_corrections_materialized(self):
        rows = authority.load_approved()
        # Calibration may append independently reviewed approvals later.
        baseline = [x for x in rows.values() if x.get("mathematical_approval_origin") == "preserved_historical_individual_source_equivalence_review"]
        self.assertEqual(len(baseline),68)
        bylabel = {r["source_label"]:r for r in baseline}
        for label in ("lemma-coherent-on-proj","lemma-coherent-on-proj-general"):
            r = bylabel[label]
            self.assertEqual(len(r["conclusions"]),5)
            self.assertEqual(r["conclusions"][0],"$X$ is a Noetherian scheme.")
            self.assertNotIn("Then $X$", " ".join(r["hypotheses"]))
        for label in ("lemma-Noetherian-permanence","lemma-obvious-Noetherian"):
            r = bylabel[label]
            self.assertEqual(r["logical_form"],"independent_conditional_claims")
            self.assertEqual(len(r["structured_cases"]),2)
            self.assertEqual(len(r["conclusions"]),2)
        for r in baseline:
            self.assertFalse(r["proof_reviewed"])
            self.assertFalse(r["published"])


if __name__ == "__main__":
    unittest.main()

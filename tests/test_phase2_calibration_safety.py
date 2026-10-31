"""Conservative Stage B source handling and preserved incident holds."""
import json
import hashlib
from pathlib import Path
import unittest

from scripts.phase2_safe_source import UnsafeSourceView, mask_source
from scripts.phase2_authoritative import content_digest, load_approved

BASE = Path("harvest/phase2_stage_b_calibration_2026-10-31")
GROUPS = ("initial_08", "bulk_09_22", "bulk_23_36", "bulk_37_50")
HOLDS = {
    "candidate.stacks.c75525d5964de744a26facaf",
    "candidate.stacks.ee19471ea886414a087bccc5",
    "candidate.stacks.46c269ee974f0198ae9e1f68",
}


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class SourceViewSafetyTests(unittest.TestCase):
    def test_situation_with_explanatory_reasoning_is_hidden(self):
        raw = (
            "\\begin{situation}\n"
            "Setup followed by an explanatory argument.\n"
            "\\end{situation}\n"
            "\\begin{lemma}\n"
            "A mathematical assertion.\n"
            "\\end{lemma}\n"
        )
        masked = mask_source(raw)
        self.assertEqual(len(masked.splitlines()), len(raw.splitlines()))
        self.assertNotIn("explanatory argument", masked)
        self.assertNotIn("\\begin{situation}", masked)
        self.assertIn("A mathematical assertion.", masked)

    def test_statement_visible_but_proof_remarks_and_outside_prose_hidden(self):
        raw = (
            "Intro: an informal proof sketch outside any environment.\n"
            "\\begin{lemma}\n"
            "\\label{lemma-test}\n"
            "If $P$, then $Q$.\n"
            "\\begin{enumerate}\n"
            "\\item First case.\n"
            "\\end{enumerate}\n"
            "\\end{lemma}\n"
            "\\begin{remark}\n"
            "Informal sketch: prohibited detail.\n"
            "\\end{remark}\n"
            "\\begin{proof}\n"
            "Formal proof: prohibited detail.\n"
            "\\end{proof}\n"
            "\\begin{definition}\n"
            "Contextual definition: allowed.\n"
            "\\end{definition}\n"
            "Narrative outside an environment: prohibited.\n"
        )
        masked = mask_source(raw)
        self.assertEqual(len(masked.splitlines()), len(raw.splitlines()))
        for token in ("\\label{lemma-test}", "If $P$, then $Q$.",
                      "\\item First case.", "Contextual definition: allowed."):
            self.assertIn(token, masked)
        for token in ("informal proof sketch", "Informal sketch",
                      "prohibited detail", "\\begin{proof}", "\\begin{remark}",
                      "Narrative outside"):
            self.assertNotIn(token, masked)

    def test_unknown_nested_environment_and_tex_comments_hidden(self):
        raw = (
            "\\begin{theorem}\n"
            "Known result. % private informal proof sketch\n"
            "\\begin{explanation}\n"
            "Proof-like explanation must be masked.\n"
            "\\end{explanation}\n"
            "Visible assertion.\n"
            "\\end{theorem}\n"
        )
        masked = mask_source(raw)
        self.assertIn("Known result.", masked)
        self.assertIn("Visible assertion.", masked)
        self.assertNotIn("private informal proof", masked)
        self.assertNotIn("Proof-like explanation", masked)
        self.assertNotIn("\\begin{explanation}", masked)

    def test_malformed_source_fails_closed(self):
        with self.assertRaises(UnsafeSourceView):
            mask_source("\\begin{lemma}\nUnfinished statement.\n")
        with self.assertRaises(UnsafeSourceView):
            mask_source("\\end{proof}\n")


class CalibrationHoldSafetyTests(unittest.TestCase):
    def test_held_candidates_stay_out_of_all_approved_records(self):
        selection = json.loads((BASE / "SELECTION.json").read_text())
        expected = {
            candidate
            for section in selection["sections"]
            for candidate in section["eligible_candidate_ids"]
        }
        approved = rows(BASE / "APPROVED_OVERLAYS.jsonl")
        approval_ids = {r["candidate_id"] for r in approved}
        correction_holds = rows(BASE / "bulk_23_36/HELD_PROOF_EXPOSURE.jsonl")
        independent_holds = rows(BASE / "bulk_23_36/INDEPENDENT_HELD_PROOF_EXPOSURE.jsonl")
        self.assertEqual(len(approved), 190)
        self.assertEqual(len(approval_ids), 190)
        self.assertEqual(len(expected), 193)
        self.assertEqual({r["candidate_id"] for r in correction_holds}, HOLDS)
        self.assertEqual({r["candidate_id"] for r in independent_holds}, HOLDS)
        self.assertEqual(expected, approval_ids | HOLDS)
        self.assertFalse(approval_ids & HOLDS)
        self.assertFalse(set(load_approved()) & HOLDS)
        for row in correction_holds:
            self.assertEqual(row["decision"], "hold_proof_context_exposure")
            self.assertTrue(row["proof_reviewed"])
            self.assertFalse(row["phase3_eligible"])
            self.assertFalse(row["published"])
        for row in independent_holds:
            self.assertEqual(row["independent_decision"], "hold_proof_context_exposure")
            self.assertTrue(row["proof_context_exposed"])
            self.assertNotIn("formulation_sha256", row)

    def test_all_calibration_approvals_have_exact_digest_binding(self):
        approved = {r["candidate_id"]: r for r in rows(BASE / "APPROVED_OVERLAYS.jsonl")}
        seen = set()
        for group in GROUPS:
            formulations = rows(BASE / group / "FORMULATIONS.jsonl")
            validations = {
                r["candidate_id"]: r
                for r in rows(BASE / group / "INDEPENDENT_VALIDATION.jsonl")
            }
            self.assertEqual({r["candidate_id"] for r in formulations}, set(validations))
            for formulation in formulations:
                cid = formulation["candidate_id"]
                self.assertNotIn(cid, seen)
                seen.add(cid)
                verdict = validations[cid]
                self.assertEqual(verdict["formulation_sha256"], content_digest(formulation))
                self.assertTrue(verdict["independent_review"])
                self.assertFalse(verdict["proof_reviewed"])
                self.assertEqual(verdict["independent_decision"], "source_equivalence_approved")
                self.assertEqual(approved[cid]["approved_content_sha256"],
                                 content_digest(approved[cid]))
                self.assertEqual(approved[cid]["independent_validation"], verdict)
                source = approved[cid]["original_source_statement_tex"].encode()
                self.assertEqual(approved[cid]["source_statement_sha256"],
                                 hashlib.sha256(source).hexdigest())
        self.assertEqual(seen, set(approved))


if __name__ == "__main__":
    unittest.main()

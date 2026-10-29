"""Tests for proof-free, deterministic Phase 2 chapter preparation."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.phase2_prepare_chapters import proof_free_lines, selected, update_index


class ChapterPreparationTests(unittest.TestCase):
    def test_proof_masks_bodies_but_preserves_source_locations(self):
        lines = [
            r"\begin{lemma} Statement \end{lemma}",
            r"\begin{proof} PRIVATE PROOF START",
            "HIDDEN MATHEMATICAL ARGUMENT",
            r"\end{proof} \begin{lemma} Next",
            r"\end{lemma}",
        ]
        result, omitted = proof_free_lines(lines)
        self.assertEqual([r["line"] for r in result], [1, 4, 5])
        self.assertNotIn("PRIVATE", str(result))
        self.assertNotIn("HIDDEN", str(result))
        self.assertIn("Next", result[1]["tex"])
        self.assertEqual(omitted, 3)

    def test_same_line_proof_does_not_leak(self):
        lines = [r"Before \begin{proof} secret \end{proof} After"]
        result, omitted = proof_free_lines(lines)
        self.assertEqual(result[0]["tex"], "Before  After")
        self.assertEqual(omitted, 1)

    def test_unbalanced_proof_fails_closed(self):
        with self.assertRaises(ValueError):
            proof_free_lines([r"\begin{proof}", "secret"])
        with self.assertRaises(ValueError):
            proof_free_lines([r"\end{proof}"])
        with self.assertRaises(ValueError):
            proof_free_lines([r"\begin{proof}\begin{proof}"])

    def test_comment_line_cannot_create_false_proof(self):
        lines = [r"Text % \begin{proof} comment", "Next"]
        result, omitted = proof_free_lines(lines)
        self.assertEqual(omitted, 0)
        self.assertEqual([x["tex"] for x in result], ["Text ", "Next"])

    def test_candidate_selection_and_incremental_skipping(self):
        chapters = ["algebra.tex", "divisors.tex", "varieties.tex"]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "algebra").mkdir()
            (out / "algebra" / "MANIFEST.json").write_text("{}")
            self.assertEqual(selected(chapters, "all", True, out, 0),
                             ["divisors.tex", "varieties.tex"])
            self.assertEqual(selected(chapters, "varieties.tex,algebra.tex", False, out, 1),
                             ["algebra.tex"])
            with self.assertRaises(ValueError):
                selected(chapters, "nonexistent.tex", True, out, 0)
            with self.assertRaises(ValueError):
                selected(chapters, "algebra.tex,algebra.tex", False, out, 0)

    def test_index_checks_content_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.assertEqual(update_index(out), (0, 0))
            idx = json.loads((out / "INDEX.json").read_text())
            self.assertTrue(idx["preparation_only"])
            self.assertFalse(idx["mathematical_approvals_added"])
            self.assertEqual(idx["prepared_chapters"], 0)


if __name__ == "__main__":
    unittest.main()

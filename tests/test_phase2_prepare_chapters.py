"""Tests for proof-free, deterministic Phase 2 chapter preparation."""
import json
import sys
from unittest.mock import patch
import tempfile
import unittest
from pathlib import Path
from scripts.phase2_prepare_chapters import proof_free_lines, selected, update_index, main


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

    def test_complete_preparation_noop_does_not_load_raw_corpus(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            chapters = [f"chapter{i:03}.tex" for i in range(115)]
            (out / "INDEX.json").write_text(json.dumps({
                "source_revision": "a04446e57ec1fbc252a871afcec7752fb2807b14",
                "prepared_chapters": 115,
                "chapters": [{"source_file": name} for name in chapters],
            }))
            for name in chapters:
                folder = out / Path(name).stem
                folder.mkdir()
                (folder / "MANIFEST.json").write_text("{}")
            argv = ["phase2_prepare_chapters", "--only-missing", "--output-dir", str(out)]
            with patch.object(sys, "argv", argv), patch(
                    "scripts.phase2_prepare_chapters.chapter_inventory",
                    side_effect=AssertionError("Must not reload 9,675 candidates")):
                main()
            (out / "chapter001" / "MANIFEST.json").unlink()
            with patch.object(sys, "argv", argv), self.assertRaisesRegex(
                    ValueError, "restore them from Git"):
                main()

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

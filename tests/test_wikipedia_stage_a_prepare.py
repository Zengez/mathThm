"""Offline structural tests for Wikipedia Stage A intake (not theorem correctness)."""
from pathlib import Path
import tempfile
import unittest

from scripts.wikipedia_stage_a_prepare import (
    TopText, clean_text, stable_id, mechanical_split, snippet, merge, dump_jsonl,
    TOTAL_LANES,
)


class WikipediaStageAPrepTests(unittest.TestCase):
    def test_parser_cuts_proof_and_preserves_latex(self):
        html = """
        <div class="mw-parser-output">
          <div class="hatnote">Not mathematical content.</div>
          <p>In mathematics, the Z test theorem states a claim about functions.</p>
          <h2 id="Statement">Statement</h2>
          <p>If a function is continuous, then its image of a compact set is
             <math alttext="{\\displaystyle \\mathrm{compact}}">fake math tree</math>.</p>
          <h2 id="Proof">Proof</h2>
          <p>Never include a long proof in the intake excerpt.</p>
        </div>"""
        parser = TopText()
        parser.feed(html)
        self.assertEqual(len(parser.blocks), 2)
        self.assertEqual(parser.blocks[1]["section"], "Statement")
        self.assertIn(r"$\mathrm{compact}$", parser.blocks[1]["text"])
        self.assertNotIn("long proof", repr(parser.blocks))
        excerpt, candidate, section = snippet(parser.blocks)
        self.assertIn("function is continuous", candidate)
        self.assertEqual(section, "Statement")
        self.assertIn("[Statement]", excerpt)

    def test_mechanical_if_then(self):
        text = "If every point of X has an open neighbourhood, then X is a topological space."
        hyp, con, state = mechanical_split(text)
        self.assertEqual(state, "mechanical_suggestion")
        self.assertIn("open neighbourhood", hyp[0])
        self.assertIn("topological space", con[0])

    def test_difficult_statement_remains_uninterpreted(self):
        for text in (
            "This is an important theorem with multiple equivalent formulations.",
            "The theorem follows from several standing assumptions.",
            "",
        ):
            hyp, con, state = mechanical_split(text)
            self.assertEqual((hyp, con, state), ([], [], "needs_interpretation"))

    def test_stable_ids(self):
        u = "https://en.wikipedia.org/wiki/Abel%E2%80%93Ruffini_theorem"
        self.assertEqual(stable_id(u), stable_id(u))
        self.assertNotEqual(stable_id(u), stable_id(u + "_other"))


if __name__ == "__main__":
    unittest.main()

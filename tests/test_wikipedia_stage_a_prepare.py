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

    def test_display_math_and_bulleted_equivalences(self):
        html = """
        <p>The next two assertions are equivalent:</p>
        <ul><li>Every substructure preserves the formula.</li>
            <li>There is an equivalent universal formula.</li></ul>
        <div><math display="block" alttext="{\\displaystyle a+b=c}">MathML</math>
             <img class="mwe-math-fallback-image-inline" alt="{\\displaystyle a+b=c}"></div>
        <h2>Proofs of the theorem</h2>
        <p>This proof should not be included.</p>
        """
        parser = TopText()
        parser.feed(html)
        texts = [b["text"] for b in parser.blocks]
        self.assertEqual(sum("a+b=c" in x for x in texts), 1)
        self.assertTrue(any("Every substructure" in x for x in texts))
        self.assertTrue(any("equivalent universal" in x for x in texts))
        self.assertFalse(any("should not be included" in x for x in texts))

    def test_explicit_result_outscores_intro_description(self):
        blocks = [
            {"section": "Lead", "kind": "p",
             "text": "In graph theory, the 2-factor theorem can be stated as follows:"},
            {"section": "Lead", "kind": "p",
             "text": "Let G be an even-regular graph. Then its edge set can be decomposed into two-factors."},
        ]
        excerpt, statement, section = snippet(blocks)
        self.assertTrue(statement.startswith("Let G be"))
        self.assertIn("2-factor theorem", excerpt)

    def test_no_vague_mechanical_split(self):
        hyp, con, status = mechanical_split(
            "Let n be a positive integer. Then the following inequality holds:")
        self.assertEqual((hyp, con, status), ([], [], "needs_interpretation"))

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

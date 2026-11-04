"""Focused structural-screen tests, intentionally not mathematical proof tests."""
import unittest

from scripts.screen_wikipedia_proof_sections import (
    SectionText, is_proof_heading, screen_stats, title_from_url, cleanup,
)


def html_stats(html):
    parser=SectionText()
    parser.feed(html)
    return parser.stats()


class WikipediaProofStructureTests(unittest.TestCase):
    def test_proof_heading_identification(self):
        for name in ("Proof", "Proofs", "Proof sketch", "Elementary proof",
                     "Proof of the theorem", "Proof by induction", "Geometric demonstration"):
            self.assertTrue(is_proof_heading(name),name)
        for name in ("References", "External links", "Historical context", "Applications",
                     "Unsolved problems", "Disproof", "History of the theorem"):
            self.assertFalse(is_proof_heading(name),name)

    def test_prose_proof_passes_without_validity_judgment(self):
        st=html_stats("""<div>
          <p>Let G be any group and suppose that a condition holds.
          By the definition of the operation, we have the stated relation.
          Therefore the required property follows by applying the previous lemma.</p>
          <p>No correctness checking is intended here.</p></div>""")
        accepted,why=screen_stats(st)
        self.assertTrue(accepted,why)

    def test_equations_and_text_pass(self):
        st=html_stats("""<div><p>Let x be the point under consideration.
        Therefore applying the identity gives the following expression.</p>
        <math alttext="{\\displaystyle f(x)=x^2+x+1}">MathML</math>
        <math alttext="{\\displaystyle f'(x)=2x+1}">MathML</math></div>""")
        self.assertTrue(screen_stats(st)[0])
        self.assertEqual(st["math_count"],2)

    def test_empty_section_fails(self):
        self.assertFalse(screen_stats(html_stats("<p>There is no proof here.</p>"))[0])
        self.assertFalse(screen_stats(html_stats("<p>See the article for proof.</p>"))[0])
        self.assertFalse(screen_stats(html_stats("<p>Proof.</p>"))[0])

    def test_nav_and_references_not_substantive(self):
        st=html_stats("""<div class="navbox">Therefore proof is shown by induction
        on the set of all graphs with enough structure and many steps.</div>
        <p>See other sources for the proof.</p>
        <sup class="reference">[15]</sup>""")
        self.assertLess(st["word_count"],15)
        self.assertFalse(screen_stats(st)[0])

    def test_proof_not_required_complete(self):
        st=html_stats("""<p>Let A be any set. Suppose the map is injective.
        By the assumption, two equal images must arise from equal elements.
        Thus the operation has the property. The omitted case is similar.</p>""")
        self.assertTrue(screen_stats(st)[0])

    def test_unicode_title(self):
        self.assertEqual(title_from_url(
          "https://en.wikipedia.org/wiki/%C5%81o%C5%9B%E2%80%93Tarski_preservation_theorem"),
            "Łoś–Tarski preservation theorem")


if __name__=="__main__":
    unittest.main()

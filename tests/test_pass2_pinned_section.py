"""Tests for exact prior Stacks Section-level notation and Pass 2 grammar."""
import unittest
from scripts.pass2_pinned_section import SECREF, interpret

RAW={"source":{"filename":"group.tex","statement_line":200,"revision":"a"*40}}
SECTIONS={("group.tex","section-notation"):{"title":"Notation","line":40,
    "complete":True,
    "text":"Let $S$ be a scheme. We fix the notation $B$ for a base object."}}
def packet(s):
    return {"candidate_id":"candidate.mock","statement":s,
            "context_status":"needs_context","hypotheses":[],"conclusions":[]}

class SectionContextTests(unittest.TestCase):
    def test_as_in_section_exact(self):
        self.assertEqual(SECREF.search(r"Let $B$ be as in Section \ref{section-notation}.").group("label"),
                        "section-notation")
    def test_recovered_section_with_then(self):
        s=(r"Let $B$ be as in Section \ref{section-notation}. "
           r"Then the functor $F$ is an equivalence.")
        v,why=interpret(packet(s),RAW,SECTIONS)
        self.assertIsNotNone(v,why)
        self.assertEqual(v["statement"],s)
        self.assertIn("notation $B$",v["local_context_used"][0]["source_statement"])
        self.assertIn("equivalence",v["conclusions"][0])
    def test_missing_section_remains_open(self):
        s=r"Let $B$ be as in Section \ref{section-unknown}. Then the functor $F$ is an equivalence."
        v,why=interpret(packet(s),RAW,SECTIONS)
        self.assertIsNone(v)
    def test_nonnotation_section_does_not_promote(self):
        s=r"Let $B$ be as in Section \ref{section-cohomology}. Then $F$ is an equivalence."
        v,why=interpret(packet(s),RAW,SECTIONS)
        self.assertIsNone(v)
    def test_section_not_earlier_does_not_promote(self):
        index={("group.tex","section-notation"):{**SECTIONS[("group.tex","section-notation")],"line":300}}
        s=r"Let $B$ be as in Section \ref{section-notation}. Then $F$ is an equivalence."
        v,why=interpret(packet(s),RAW,index)
        self.assertIsNone(v)
    def test_multiple_source_inheritance_rejected(self):
        s=(r"Let $B$ be as in Section \ref{section-notation}. "
           r"Let $F$ be as in Lemma \ref{lemma-F}. Then $F$ is an equivalence.")
        v,why=interpret(packet(s),RAW,SECTIONS)
        self.assertIsNone(v)

if __name__=="__main__":
    unittest.main()

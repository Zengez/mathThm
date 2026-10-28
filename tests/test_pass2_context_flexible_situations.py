"""Pinned named Situation embedded-clause Pass 2 regression tests."""
import unittest
from scripts.pass2_context_flexible_situations import interpret

def raw():
    return {"source":{"filename":"sample.tex","revision":"a"*40}}
def row(s):
    return {"statement":s,"context_status":"needs_context","hypotheses":[],"conclusions":[]}
CONTEXT={("sample.tex","situation-A"):{
    "kind":"situation","text":"Let $S$ be a scheme. Assume $S$ is Noetherian.","line":50}}

class FlexibleSituationTests(unittest.TestCase):
    def test_embedded_situation_and_then(self):
        s=r"Let $(S,\delta)$ be as in Situation \ref{situation-A}. Let $X$ be a scheme. Then $X$ is a scheme."
        v,why=interpret(row(s),raw(),CONTEXT)
        self.assertIsNotNone(v,why)
        self.assertIn("Noetherian",v["hypotheses"][0])
        self.assertIn("Let $X$",v["hypotheses"][1])
        self.assertIn("$X$ is a scheme",v["conclusions"][0])

    def test_list_conditional_source_cases(self):
        s=(r"In Situation \ref{situation-A}. "
           r"\begin{enumerate}\item If $P$ then $Q$."
           r"\item If $R$ then $S$.\end{enumerate}")
        v,why=interpret(row(s),raw(),CONTEXT)
        self.assertIsNotNone(v,why)
        self.assertEqual(len(v["structured_cases"]),2)
        self.assertTrue(any("If $P$" in h for h in v["hypotheses"]))
        self.assertTrue(any("$Q$" in c for c in v["conclusions"]))

    def test_source_requires_actual_named_situation(self):
        s=r"Let $S$ be as in Situation \ref{situation-B}. Then $P$."
        v,why=interpret(row(s),raw(),CONTEXT)
        self.assertIsNone(v)

    def test_iff_respects_both_sides(self):
        s=(r"Let $X$ be as in Situation \ref{situation-A}. "
           r"The following are equivalent: \begin{enumerate}"
           r"\item $X$ is $P$.\item $X$ is $Q$.\end{enumerate}")
        v,why=interpret(row(s),raw(),CONTEXT)
        self.assertIsNotNone(v,why)
        self.assertTrue(all(x[0] in v["hypotheses"] and x[0] in v["conclusions"]
            for x in v["equivalence_sides"]))

    def test_no_silent_other_context(self):
        s=(r"Let $S$ be as in Situation \ref{situation-A}. "
           r"With notation as above, then $P$.")
        v,why=interpret(row(s),raw(),CONTEXT)
        self.assertIsNone(v)

if __name__=="__main__":
    unittest.main()

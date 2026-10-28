"""Statement-only pinned Stacks Situation Pass 2 tests."""
import unittest
from scripts.pass2_context_expansion import REF,split_source,prepare

class SourceSituationTests(unittest.TestCase):
    def test_exact_situation_reference(self):
        m=REF.match(r"In Situation \ref{situation-flat-at-point}. If $P$ then $Q$.")
        self.assertIsNotNone(m)
        self.assertEqual(m.group("label"),"situation-flat-at-point")

    def test_header_plus_then_split(self):
        out,why=split_source(r"Then $f$ is flat.")
        self.assertIsNotNone(out,why)
        self.assertEqual(out["conclusions"],["$f$ is flat."])

    def test_explicit_if_then_under_context(self):
        out,why=split_source(r"If $R$ is reduced, then $X$ is reduced.")
        self.assertIsNotNone(out,why)
        self.assertIn("If $R$",out["hypotheses"][0])
        self.assertIn("$X$",out["conclusions"][0])

    def test_iff_is_both_columns(self):
        out,why=split_source(r"The following are equivalent: \begin{enumerate}\item $P$.\item $Q$.\end{enumerate}")
        self.assertIsNotNone(out,why)
        self.assertEqual(out["hypotheses"],out["conclusions"])

    def test_source_situation_contributes_pinned_context(self):
        old={"candidate_id":"candidate.test","statement":"In Situation ...","area":"Example"}
        info={"text":"Let $R$ be a ring. Assume $R$ is reduced.","kind":"situation","line":10}
        out=prepare(old,info,"situation-A","foo.tex","a"*40,"If $P$ then $Q$",
                    {"hypotheses":["If $P$"],"conclusions":["$Q$"],"logical_form":"implication"},
                    "explicit If")
        self.assertEqual(out["context_status"],"resolved")
        self.assertEqual(out["statement"],old["statement"])
        self.assertIn("Assume $R$ is reduced",out["hypotheses"][0])
        self.assertEqual(out["local_context_used"][0]["source_revision"],"a"*40)
        self.assertEqual(out["conclusions"],["$Q$"])

    def test_lone_ambiguous_condition_not_resolved(self):
        out,reason=split_source("Suppose $X$ is flat.")
        self.assertIsNone(out)

if __name__=="__main__":
    unittest.main()

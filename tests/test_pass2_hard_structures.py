"""Regression tests for difficult Pass 2 source structure; NO proof validation."""
import unittest
from scripts.pass2_hard_structures import interpret, enum_blocks, list_items, mask_math

def make(s):
    return {"statement":s}

class HardStructuresTests(unittest.TestCase):
    def assertInterpret(self,text,kind):
        out,why=interpret(make(text))
        self.assertIsNotNone(out,why)
        self.assertEqual(out["logical_form"],kind)
        return out

    def test_equivalence_preserves_all_sides_and_bidirectionality(self):
        s=r"Let $M$ be an $R$-module. The following are equivalent:"+"\n"+r"\begin{enumerate}"+"\n"+r"\item $M$ is flat."+"\n"+r"\item Tensoring with $M$ preserves injections."+"\n"+r"\end{enumerate}"
        out=self.assertInterpret(s,"equivalence")
        self.assertEqual(len(out["equivalence_sides"]),2)
        self.assertIn("equivalent",out["conclusions"][0])
        self.assertIn("$M$",out["hypotheses"][0])

    def test_equivalence_with_add_more_here_is_deferred(self):
        s="Let $X$ be a spectral space. The following are equivalent:\n"+r"\begin{enumerate}\item $X$ is profinite.\item add more here.\end{enumerate}"
        out,why=interpret(make(s))
        self.assertIsNone(out)
        self.assertIn("editorial",why)

    def test_equivalence_with_moreover_is_deferred(self):
        s="Let $X$ be a space. The following are equivalent:\n"+r"\begin{enumerate}\item $P$.\item $Q$.\end{enumerate}"+"\nMoreover, in this case $S$."
        out,why=interpret(make(s))
        self.assertIsNone(out)
        self.assertIn("additional",why)

    def test_list_of_conditional_clauses_keeps_conditions(self):
        s=r"Let $X$ be a topological space."+"\n"+r"\begin{enumerate}\item If $X$ is compact, then $X$ is quasi-compact.\item If $X$ is Hausdorff, then $X$ is sober.\end{enumerate}"
        out=self.assertInterpret(s,"conjunction_of_source_clauses")
        self.assertEqual(len(out["conclusions"]),2)
        self.assertEqual(len(out["structured_cases"]),2)
        self.assertTrue(out["structured_cases"][0]["clause_is_conditional"])
        self.assertIn("If $X$ is compact",out["conclusions"][0])

    def test_nested_enumeration_not_flattened(self):
        s=r"Let $X$ be a space. Then \begin{enumerate}\item $P$.\item If $Q$ then \begin{enumerate}\item $R$\end{enumerate}\end{enumerate}"
        out=self.assertInterpret(s,"conjunction_of_source_clauses")
        self.assertEqual(len(out["conclusions"]),2)
        self.assertIn(r"\begin{enumerate}",out["conclusions"][1])

    def test_two_separate_enumerations_with_then(self):
        s=r"Let $X$ be a space. Assume \begin{enumerate}\item $P$.\end{enumerate} Then \begin{enumerate}\item $Q$.\end{enumerate}"
        out=self.assertInterpret(s,"implication_with_structured_clauses")
        self.assertIn("Assume",out["hypotheses"][0])

    def test_multiple_enumerations_without_outer_then_deferred(self):
        s=r"Let $X$ be a space. \begin{enumerate}\item $P$\end{enumerate} \begin{enumerate}\item $Q$\end{enumerate}"
        out,why=interpret(make(s))
        self.assertIsNone(out)

    def test_source_setup_then_claim(self):
        s=r"Let $X$ be a scheme. Let $f:X\to Y$ be a map. For any point $x$, there exists a preimage."
        out=self.assertInterpret(s,"source_setup_then_assertion")
        self.assertIn("Let $f",out["hypotheses"][0])
        self.assertIn("For any",out["conclusions"][0])

    def test_short_universal_assertion(self):
        s="Any surjective endomorphism of a Noetherian ring is an isomorphism."
        out=self.assertInterpret(s,"source_universal_predicate")
        self.assertIn("surjective endomorphism",out["hypotheses"][0])
        self.assertEqual(out["conclusions"][0],s)

    def test_context_deferred(self):
        s=r"Under the assumptions of Lemma \ref{foo}, the claim holds."
        out,why=interpret(make(s))
        self.assertIsNone(out)
        self.assertIn("context",why)

    def test_math_equation_does_not_break_setup(self):
        s=r"Let $f$ be a map. If $a.b$ occurs in the equation, the map is continuous."
        out=self.assertInterpret(s,"source_setup_then_assertion")
        self.assertTrue(out["conclusions"][0].startswith("If "))

    def test_not_routinely_split_all_lists(self):
        s=r"Let $X$ be a space. In each of the following cases $X$ is compact: \begin{enumerate}\item $X$ is finite\item $X$ is a point\end{enumerate}"
        out,why=interpret(make(s))
        self.assertIsNone(out)
        self.assertIn("cases",why)

if __name__=="__main__":
    unittest.main()

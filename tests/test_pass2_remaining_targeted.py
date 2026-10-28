"""Source-only Pass 2 targeted review rules, with no proof analysis."""
import unittest
from scripts.pass2_remaining_targeted import interpret_targeted, source_body

def packet(s):
    return {"candidate_id":"candidate.stacks.mock","statement":s,
            "hypotheses":[],"conclusions":[],"context_status":"needs_structure"}

class RemainingTargetedTests(unittest.TestCase):
    def test_simple_iff_is_indexed_both_ways(self):
        s=r"A scheme $X$ is integral if and only if it is reduced and irreducible."
        v,_=interpret_targeted(packet(s))
        self.assertIsNotNone(v)
        self.assertEqual(v["logical_form"],"equivalence")
        self.assertEqual(v["hypotheses"],v["conclusions"])
        self.assertEqual(len(v["equivalence_sides"]),2)

    def test_reference_metadata_retained_outside_search(self):
        s=(r"\begin{reference}\cite{Reference}\end{reference}"
           "\n"+r"A ring $R$ is Jacobson if and only if $\Spec(R)$ is Jacobson.")
        body,removed=source_body(s)
        self.assertTrue(removed)
        self.assertFalse(body.startswith(r"\begin{reference}"))
        v,_=interpret_targeted(packet(s))
        self.assertIsNotNone(v)
        self.assertEqual(v["statement"],s)

    def test_explicit_assumption_list_then_conclusion(self):
        s=(r"Let $X$ be a scheme. Assume "
           r"\begin{enumerate}\item $X$ is reduced.\item $X$ is Noetherian."
           r"\end{enumerate} Then $X$ is a scheme.")
        v,_=interpret_targeted(packet(s))
        self.assertIsNotNone(v)
        self.assertEqual(v["logical_form"],"implication_with_enumerated_premises")
        self.assertIn("reduced",v["hypotheses"][0])
        self.assertIn("Then",v["structured_cases"][0]["source_clause"])

    def test_iff_after_assumption_list_is_bidirectional(self):
        s=(r"Let $X$ be a scheme. Assume "
           r"\begin{enumerate}\item $X$ is reduced.\end{enumerate}"
           r" Then $X$ is compact if and only if $X$ is quasi-compact.")
        v,_=interpret_targeted(packet(s))
        self.assertIsNotNone(v)
        self.assertEqual(v["logical_form"],"equivalence_with_enumerated_premises")
        self.assertEqual(v["hypotheses"][1:],v["conclusions"])

    def test_alternative_cases_do_not_merge_assumptions(self):
        s=(r"Let $X$ be a scheme. In each of the following cases "
           r"$X$ has an open point: "
           r"\begin{enumerate}\item $X$ is finite.\item $X$ is a singleton."
           r"\end{enumerate}")
        v,_=interpret_targeted(packet(s))
        self.assertIsNotNone(v)
        self.assertEqual(v["logical_form"],"alternative_sufficient_conditions")
        self.assertEqual(len(v["structured_cases"]),2)

    def test_unfinished_editorial_statement_is_not_accepted(self):
        s=(r"Let $X$ be a space. The following are equivalent: "
           r"\begin{enumerate}\item $P$.\item add more here.\end{enumerate}")
        v,_=interpret_targeted(packet(s))
        self.assertIsNone(v)

    def test_context_dependency_must_remain_open(self):
        s=r"With the notation of Lemma \ref{foo}, the diagram is commutative."
        v,_=interpret_targeted(packet(s))
        self.assertIsNone(v)

    def test_no_dummy_hypothesis_for_unconditional_existence(self):
        s=r"There exists a ring with this property."
        v,_=interpret_targeted(packet(s))
        self.assertIsNone(v)

    def test_source_premise_followed_by_existential(self):
        s=r"Let $X$ be a scheme and $U\subset X$ open; there exists an open cover of $X$."
        v,_=interpret_targeted(packet(s))
        self.assertIsNotNone(v)
        self.assertIn("exists",v["conclusions"][0])

if __name__=="__main__":
    unittest.main()

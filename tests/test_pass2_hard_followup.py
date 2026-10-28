"""Follow-up Pass 2 tests: source structure only; no proof scanning."""
import unittest
from scripts.pass2_hard_followup import interpret_followup, repair_existing_cases
from scripts.pass2_hard_structures import logical_item

def item(s): return {"statement":s,"hypotheses":[],"conclusions":[]}

class FollowupPass2Tests(unittest.TestCase):
    def test_equivalence_with_moreover_keeps_both_search_sides(self):
        s=(r"Let $X$ be a space. The following are equivalent "
           r"\begin{enumerate}\item $X$ is compact.\item $X$ is quasi-compact.\end{enumerate}"
           r" Moreover, in this case $X$ is sober.")
        o,n=interpret_followup(item(s))
        self.assertIsNotNone(o,n)
        self.assertEqual(o["logical_form"],"equivalence_with_additional_assertion")
        self.assertEqual(o["hypotheses"][1:3],o["conclusions"][:2])
        self.assertIn("Moreover",o["conclusions"][2])

    def test_equivalence_without_setup_is_bidirectional(self):
        s=r"The following are equivalent: \begin{enumerate}\item $P$.\item $Q$.\end{enumerate}"
        o,n=interpret_followup(item(s))
        self.assertIsNotNone(o,n)
        self.assertEqual(o["hypotheses"],o["conclusions"])

    def test_source_placeholder_defers(self):
        s=(r"Let $X$ be a space. The following are equivalent "
           r"\begin{enumerate}\item $P$.\item add more here.\end{enumerate}")
        o,n=interpret_followup(item(s))
        self.assertIsNone(o)

    def test_iff_both_fields(self):
        s=r"A ring $R$ is Jacobson if and only if $\Spec(R)$ is Jacobson."
        o,n=interpret_followup(item(s))
        self.assertIsNotNone(o,n)
        self.assertEqual(o["hypotheses"],o["conclusions"])

    def test_conditional_subcase_produces_correct_local_search(self):
        o=logical_item("If $P$, then $Q$.","Let $X$ be a space.")
        self.assertEqual(o["logical_form"],"conditional_subcase")
        self.assertIn("If $P$",o["hypotheses"][1])
        self.assertEqual(o["conclusions"],["$Q$."])

    def test_biconditional_subcase_goes_both_ways(self):
        o=logical_item("$P$ if and only if $Q$.","Let $X$ be a space.")
        self.assertEqual(o["logical_form"],"equivalence_subcase")
        self.assertEqual(o["hypotheses"][1:],o["conclusions"])

    def test_previous_case_repairs_source(self):
        o=repair_existing_cases({
            "logical_form":"conjunction_of_source_clauses",
            "hypotheses":["Let $X$ be a space."],
            "conclusions":["If $P$ then $Q$."],
            "structured_cases":[{"hypotheses":["Let $X$ be a space."],
                                 "conclusions":["If $P$ then $Q$."],
                                 "clause_is_conditional":True}]})
        self.assertIsNotNone(o)
        self.assertEqual(o["conclusions"],["$Q$."])
        self.assertIn("If $P$",o["hypotheses"][1])

    def test_context_stays_unresolved(self):
        o,n=interpret_followup(item(r"In Situation \ref{foo}, the following are equivalent: \begin{enumerate}\item $P$.\item $Q$.\end{enumerate}"))
        self.assertIsNone(o)

if __name__=="__main__":
    unittest.main()

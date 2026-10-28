"""Source semantic Pass 2 regression tests; statement reading only."""
import unittest
from scripts.pass2_semantic_statements import try_one

def pkt(s):
    return {"candidate_id":"candidate.mock","statement":s,
            "context_status":"needs_structure","hypotheses":[],"conclusions":[]}

class SemanticSourceTests(unittest.TestCase):
    def test_base_change_preserves_condition(self):
        s="The base change of a morphism which is syntomic is syntomic."
        v,reason=try_one(pkt(s))
        self.assertIsNotNone(v,reason)
        self.assertEqual(v["logical_form"],"source_closure_property")
        self.assertIn("which is syntomic",v["hypotheses"][0])
        self.assertEqual(v["conclusions"],[s])

    def test_composition_with_respectively_is_not_flattened(self):
        s=(r"Compositions of integral, resp.\ finite morphisms of algebraic "
           r"stacks are integral, resp.\ finite.")
        v,why=try_one(pkt(s))
        self.assertIsNotNone(v,why)
        self.assertIn("resp.",v["hypotheses"][0])
        self.assertEqual(v["conclusions"],[s])

    def test_same_holds_second_property_is_kept_as_source_case(self):
        s=("The base change of a morphism which is unramified is unramified. "
           "The same holds for G-unramified morphisms.")
        v,why=try_one(pkt(s))
        self.assertIsNotNone(v,why)
        self.assertEqual(len(v["structured_cases"]),2)
        self.assertEqual(len(v["conclusions"]),2)

    def test_casewise_alternatives_not_all_jointly_required(self):
        s=(r"Let $X$ be a scheme. "
           r"In each of the following cases $X$ has a regular section:"
           r"\begin{enumerate}\item $X$ is integral."
           r"\item $X$ is Noetherian.\end{enumerate}")
        v,why=try_one(pkt(s))
        self.assertIsNotNone(v,why)
        self.assertEqual(v["logical_form"],"source_alternative_sufficient_conditions")
        self.assertEqual(len(v["structured_cases"]),2)
        self.assertNotIn("Noetherian",v["structured_cases"][0]["hypotheses"][1])

    def test_case_with_editorial_placeholder_is_deferred(self):
        s=(r"The following types of schemes are J-2."
           r"\begin{enumerate}\item Schemes over fields."
           r"\item And so on.\end{enumerate}")
        v,reason=try_one(pkt(s))
        self.assertIsNone(v)

    def test_simple_source_enumerated_conditional_results(self):
        s=(r"Elementary properties. Let $k$ be a field. Let $S$ be a $k$-algebra."
           r"\begin{enumerate}\item If $S$ is geometrically reduced, then "
           r"its localizations are geometrically reduced."
           r"\item A directed colimit of geometrically reduced algebras "
           r"is geometrically reduced.\end{enumerate}")
        v,reason=try_one(pkt(s))
        self.assertIsNotNone(v,reason)
        self.assertEqual(v["logical_form"],"source_enumerated_assertions")
        self.assertEqual(v["structured_cases"][0]["logical_form"],"conditional_subcase")

    def test_let_setup_with_this_map_assertion(self):
        s=(r"Let $S$ be a scheme. Consider the map $f:X \to Y$. "
           r"This map is injective.")
        v,why=try_one(pkt(s))
        self.assertIsNotNone(v,why)
        self.assertEqual(v["logical_form"],"source_setup_followed_by_assertion")
        self.assertIn("This map",v["conclusions"][0])

    def test_unconditional_existence_must_remain_open(self):
        s=r"There exists a quasi-compact scheme without any separated dense open."
        v,why=try_one(pkt(s))
        self.assertIsNone(v)

    def test_equivalence_not_treated_as_plain_setup_assertion(self):
        s=(r"Let $X$ be a scheme. The following are equivalent "
           r"\begin{enumerate}\item $X$ is reduced.\item $X$ is integral.\end{enumerate}")
        v,why=try_one(pkt(s))
        self.assertIsNone(v)

if __name__=="__main__":
    unittest.main()

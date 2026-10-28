"""Pass 2 statement semantic QC tests, no proof examination."""
import unittest
from scripts.pass2_semantic_qc import (requeue,repair_composite,
    repair_iff,repair_parallel,repair_implicit_if)
from scripts.pass2_semantic_statements import try_one

class SemanticQcTests(unittest.TestCase):
    def test_bad_graph_item_with_orphan_are_given_by_is_deferred(self):
        s=(r"Classification of graph shape. Let $n>8$. Then we have the $m$'s "
           r"\begin{enumerate}\item are given by $(1,2,3)$.\end{enumerate}")
        v,_=try_one({"statement":s,"context_status":"needs_structure",
                     "hypotheses":[],"conclusions":[]})
        self.assertIsNone(v)

    def test_bad_conjunction_iff_is_not_split_as_simple_asserted_items(self):
        s=(r"Let $\Lambda$ be a ring. Then $K$ is perfect if and only if "
           r"the two following conditions hold:\begin{enumerate}"
           r"\item $K$ has finite Tor dimension."
           r"\item $H^i(K)$ is finite.\end{enumerate}")
        v,_=try_one({"statement":s,"context_status":"needs_structure",
                     "hypotheses":[],"conclusions":[]})
        self.assertIsNone(v)

    def test_requeue_clears_all_search_fields(self):
        original={"hypotheses":["foo"],"conclusions":["bar"],
                  "context_status":"resolved","logical_form":"placeholder"}
        v=requeue(original,"scope unknown")
        self.assertEqual(v["hypotheses"],[])
        self.assertEqual(v["conclusions"],[])
        self.assertEqual(v["context_status"],"needs_structure")
        self.assertIn("scope unknown",v["context_note"])

    def test_composition_subject_does_not_include_conclusion(self):
        s=("The composition of morphisms of algebraic stacks which satisfy "
           "the existence part of the valuative criterion is another "
           "morphism of algebraic stacks which satisfies the existence part.")
        v=repair_composite({"statement":s})
        self.assertIsNotNone(v)
        self.assertTrue(v["hypotheses"][0].endswith("valuative criterion"))
        self.assertNotIn("is another",v["hypotheses"][0])
        self.assertEqual(v["conclusions"][0],s)

    def test_conjunctive_side_is_a_single_equivalence_condition(self):
        s=(r"Let $\Lambda$ be a left Noetherian ring and $K\in D(\Lambda)$. "
           r"Then $K$ is perfect if and only if the two following conditions hold:"
           r"\begin{enumerate}\item $K$ has finite Tor dimension."
           r"\item $H^i(K)$ is finite.\end{enumerate}")
        v=repair_iff({"statement":s})
        self.assertIsNotNone(v)
        self.assertEqual(len(v["equivalence_sides"]),2)
        self.assertEqual(len(v["conclusions"]),2)
        self.assertIn(r"\begin{enumerate}",v["conclusions"][1])

    def test_parallel_source_claim_subject(self):
        row={"statement":("The composition of two morphisms which are unramified "
                "is unramified. The same holds for G-unramified morphisms."),
             "hypotheses":["two morphisms which are unramified",
                           "source follow-up property: The same holds for G-unramified morphisms."],
             "structured_cases":[{"hypotheses":["two morphisms which are unramified"]},
                                 {"hypotheses":["source follow-up property: ..."]}]}
        v=repair_parallel(row)
        self.assertEqual(v["hypotheses"][1],"G-unramified morphisms")
        self.assertEqual(v["structured_cases"][1]["hypotheses"],["G-unramified morphisms"])

    def test_implicit_so_is_conditional(self):
        row={"statement":"If $S$ is geometrically reduced over $k$ so is every k-subalgebra.",
             "hypotheses":["Let $S$ be a $k$-algebra."],
             "conclusions":["If $S$ is geometrically reduced over $k$ so is every subalgebra.","other","other","other"],
             "structured_cases":[{"source_clause":"If $S$ is geometrically reduced over $k$ so is every subalgebra."},
                                 {"source_clause":"foo"},{"source_clause":"bar"},{"source_clause":"baz"}]}
        v=repair_implicit_if(row)
        self.assertIsNotNone(v)
        self.assertEqual(v["structured_cases"][0]["logical_form"],"conditional_subcase")
        self.assertIn("subalgebra",v["conclusions"][0])

if __name__=="__main__":
    unittest.main()

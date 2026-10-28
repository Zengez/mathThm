"""Regression tests for bounded Pass 2 remaining structural semantics."""
import unittest
from scripts.pass2_deep_structural import try_hard

def item(s):
    return {"statement":s,"context_status":"needs_structure",
            "hypotheses":[],"conclusions":[]}

class DeepStructuralTests(unittest.TestCase):
    def test_source_label_metadata_not_a_premise(self):
        s=(r"\begin{reference}\cite{EGA}\end{reference} "
            r"Let $X$ be a scheme. Then $X$ is quasi-compact.")
        v,why=try_hard(item(s))
        self.assertIsNotNone(v,why)
        self.assertEqual(v["statement"],s)
        self.assertIn("Let",v["hypotheses"][0])

    def test_equivalence_with_in_this_case_tail(self):
        s=(r"Let $X$ be a topological space. The following are equivalent: "
           r"\begin{enumerate}\item $X$ is compact.\item $X$ is quasi-compact."
           r"\end{enumerate} In this case $X$ has property $P$.")
        v,why=try_hard(item(s))
        self.assertIsNotNone(v,why)
        self.assertEqual(v["logical_form"],"equivalence_with_scoped_consequence")
        self.assertEqual(v["hypotheses"][1:3],v["conclusions"][:2])
        self.assertIn("In this case",v["conclusions"][2])

    def test_source_enumerated_sufficient_types(self):
        s=(r"The following types of schemes are J-2: "
           r"\begin{enumerate}\item Schemes over fields."
           r"\item Schemes over complete local rings.\end{enumerate}")
        v,why=try_hard(item(s))
        self.assertIsNotNone(v,why)
        self.assertEqual(v["logical_form"],"source_classification_list")
        self.assertEqual(len(v["structured_cases"]),2)

    def test_source_introduction_followed_by_existential_result(self):
        s=(r"Let $X$ be a topological space. Let $U$ be open. "
           r"There exists a cover of $X$ such that "
           r"\begin{enumerate}\item $U$ is in the cover.\end{enumerate}")
        v,why=try_hard(item(s))
        self.assertIsNotNone(v,why)
        self.assertIn("There exists",v["conclusions"][0])

    def test_reverse_if_indexes_antecedent_correctly(self):
        s=r"A map $f$ is injective if $f(x)=f(y)$ implies $x=y$."
        v,why=try_hard(item(s))
        self.assertIsNotNone(v,why)
        self.assertIn("If",v["hypotheses"][0])
        self.assertIn("injective",v["conclusions"][0])

    def test_multiple_unconditional_sentences_keep_source_cases(self):
        s=r"A finite Jacobson space is discrete. A Jacobson space with finitely many closed points is discrete."
        v,why=try_hard(item(s))
        self.assertIsNotNone(v,why)
        self.assertEqual(v["logical_form"],"collection_of_source_assertions")
        self.assertEqual(len(v["structured_cases"]),2)

    def test_unconditional_existence_not_given_dummy_antecedent(self):
        s=r"There exists a quasi-compact scheme without a separated dense open."
        v,why=try_hard(item(s))
        self.assertIsNone(v)

    def test_unfinished_statement_stays_open(self):
        s=(r"The following types of schemes are J-2: "
            r"\begin{enumerate}\item Schemes over fields.\item And so on."
            r"\end{enumerate}")
        v,why=try_hard(item(s))
        self.assertIsNone(v)

if __name__=="__main__":
    unittest.main()

"""Pass 2 classification/split tests; tests syntax, not mathematical truth."""
import unittest
from scripts.pass2_fast_stacks import classify, clean_statement, grammatical_split

def candidate(s, label="lemma-test", kind="lemma", file="algebra.tex"):
    return {"candidate_id":"candidate.stacks.test",
            "entry_type":kind,"statement_tex":r"\label{"+label+"}\n"+s,
            "detected_local_references":[],
            "source":{"label":label,"filename":file}}


class FastPass2Tests(unittest.TestCase):
    def test_if_then_with_assumptions(self):
        d=classify(candidate(r"Let $R\to S$ be a ring map. Let $M$ be an $S$-module. If $M$ is finite as an $R$-module, then $M$ is finite as an $S$-module."))
        self.assertEqual(d["context_status"],"resolved")
        self.assertIn("$R\\to S$",d["hypotheses"][0])
        self.assertIn("finite as an $S$-module",d["conclusions"][0])
        self.assertEqual(d["split_confidence"],"syntax_only")
        self.assertEqual(d["result_classification"],"mathematical_result")

    def test_clear_then(self):
        d=classify(candidate(r"Let $X$ be a compact space. Then $X$ is quasi-compact.",file="topology.tex"))
        self.assertEqual(d["context_status"],"resolved")
        self.assertIn("quasi-compact",d["conclusions"][0])

    def test_labeled_no_boundary_goes_to_structure_queue(self):
        d=classify(candidate(r"The category $\mathcal C$ has a terminal object."))
        self.assertEqual(d["context_status"],"needs_structure")
        self.assertEqual(d["result_classification"],"mathematical_result")

    def test_reference_to_inherited_notation_remains_unresolved(self):
        d=classify(candidate(r"With notation as in Lemma \ref{lemma-prior}, let $X$ be a scheme. Then $X$ has property $P$."))
        self.assertEqual(d["context_status"],"needs_context")
        self.assertEqual(d["hypotheses"],[])

    def test_enumeration_not_flattened(self):
        d=classify(candidate("\\\\begin{enumerate}\n\\\\item $P$.\n\\\\item $Q$.\n\\\\end{enumerate}"))
        self.assertEqual(d["context_status"],"needs_structure")

    def test_questions_are_flagged_uncertain(self):
        d=classify(candidate("Open question: is every ring Noetherian?"))
        self.assertEqual(d["context_status"],"needs_classification")
        self.assertEqual(d["result_classification"],"uncertain")

    def test_missing_label_not_declared_result(self):
        d=classify(candidate("If $P$, then $Q$.",label=None))
        self.assertEqual(d["context_status"],"needs_classification")

    def test_label_and_slogan_removed_without_rewriting_theorem(self):
        s=clean_statement(r"\label{lemma-x}"+"\n"+r"\begin{slogan}A hint\end{slogan}"+"\n"+r"Let $X$ be compact. Then $X$ is quasi-compact.")
        self.assertNotIn("label",s)
        self.assertNotIn("slogan",s)
        self.assertIn("Then $X$",s)

    def test_proof_is_not_accessed(self):
        d=classify(candidate("Let $X$ be a ring. Then $X$ is a ring."))
        self.assertNotIn("proof",d)


if __name__=="__main__":
    unittest.main()

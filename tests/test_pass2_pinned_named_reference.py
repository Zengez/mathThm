"""Pass 2 pinned Stacks named theorem reference tests: no proof inspection."""
import unittest
from scripts.pass2_pinned_named_reference import source_grammar,interpret,extract_setup_from_reference

SOURCE={"source":{"filename":"sample.tex","statement_line":1000,
   "revision":"a"*40}}
CTX={("sample.tex","lemma-construction"):{
    "kind":"lemma","line":900,
    "text":r"Let $R$ be a ring. Let $E$ be a module. Then there exists a functor $F$."}}
def packet(s):
    return {"candidate_id":"candidate.mock","statement":s,
            "context_status":"needs_context","hypotheses":[],"conclusions":[]}

class NamedReferenceTests(unittest.TestCase):
    def test_source_native_then(self):
        s=r"Let $E$ be as in Lemma \ref{lemma-construction}. Then $F(E)$ is nonzero."
        v,why=interpret(packet(s),SOURCE,CTX)
        self.assertIsNotNone(v,why)
        self.assertEqual(v["context_status"],"resolved")
        self.assertIn("nonzero",v["conclusions"][0])
        self.assertEqual(v["statement"],s)
        self.assertEqual(v["local_context_used"][0]["inherited_setup"],
                         r"Let $R$ be a ring. Let $E$ be a module.")

    def test_reference_result_not_copied_as_hypothesis(self):
        s=r"Let $E$ be as in Lemma \ref{lemma-construction}. Then $F(E)$ is nonzero."
        v,_=interpret(packet(s),SOURCE,CTX)
        self.assertNotIn("there exists a functor",v["hypotheses"][0])

    def test_biconditional_preserved_as_both_search_sides(self):
        s=(r"Let $E$ be as in Lemma \ref{lemma-construction}. "
           r"Then $P$ if and only if $Q$.")
        v,why=interpret(packet(s),SOURCE,CTX)
        self.assertIsNotNone(v,why)
        self.assertEqual(v["hypotheses"][1:],v["conclusions"])
        self.assertEqual(v["logical_form"],"pinned_named_reference_conditional_equivalence")

    def test_enumerated_equivalence_recovered(self):
        s=(r"Let $E$ be as in Lemma \ref{lemma-construction}. "
           r"The following are equivalent: \begin{enumerate}"
           r"\item $P$.\item $Q$.\end{enumerate}")
        v,why=interpret(packet(s),SOURCE,CTX)
        self.assertIsNotNone(v,why)
        self.assertEqual(v["hypotheses"][1:],v["conclusions"])

    def test_out_of_order_reference_stays_pending(self):
        late={("sample.tex","lemma-construction"):{
            "kind":"lemma","line":1005,
            "text":r"Let $X$ be a scheme. Then the functor $F$ exists."}}
        s=r"Let $E$ be as in Lemma \ref{lemma-construction}. Then $P$."
        v,why=interpret(packet(s),SOURCE,late)
        self.assertIsNone(v)
        self.assertIn("earlier",why)

    def test_unknown_reference_remains_open(self):
        s=r"Let $E$ be as in Lemma \ref{lemma-else}. Then $P$."
        v,why=interpret(packet(s),SOURCE,CTX)
        self.assertIsNone(v)

    def test_unresolved_above_remains_open(self):
        s=r"Let $E$ be as above in Lemma \ref{lemma-construction}. Then $P$."
        v,why=interpret(packet(s),SOURCE,CTX)
        self.assertIsNone(v)

    def test_multiple_top_level_then_requires_review(self):
        s=(r"Let $E$ be as in Lemma \ref{lemma-construction}. "
           r"Then if $P$ then $Q$.")
        v,why=interpret(packet(s),SOURCE,CTX)
        self.assertIsNone(v)

    def test_no_fake_unconditional_premise(self):
        parsed,reason=source_grammar(
            r"There exists an example as in Lemma \ref{lemma-construction}.")
        self.assertIsNone(parsed)

if __name__=="__main__":
    unittest.main()

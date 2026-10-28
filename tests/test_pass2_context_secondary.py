"""Tests for source-only secondary Pass 2 context decisions."""
import unittest
from scripts.pass2_context_secondary import try_secondary

def mk(s):
    return {"statement":s,"context_status":"needs_context",
            "hypotheses":[],"conclusions":[]}
SOURCE={"source":{"filename":"math.tex","revision":"a"*40}}

class SecondaryContextTests(unittest.TestCase):
    def test_metadata_only_false_alarm(self):
        s=(r"\begin{reference}Compare in the setting of topology.\end{reference}"
           "\nLet $X$ be a scheme. Then $X$ is a scheme.")
        v,reason=try_secondary(mk(s),SOURCE,{})
        self.assertIsNotNone(v,reason)
        self.assertEqual(v["statement"],s)
        self.assertEqual(reason,"metadata_only")

    def test_real_named_lemma_recovers_only_setup(self):
        s=(r"Assumptions and notation as in Lemma \ref{lemma-D}. "
           r"Let $I$ be an ideal. Then $D(I)$ is a module.")
        idx={("math.tex","lemma-D"):{
            "text":r"Let $R$ be a ring. Let $D$ be a functor. Then $D(R)$ is a module.",
            "kind":"lemma","line":30}}
        v,reason=try_secondary(mk(s),SOURCE,idx)
        self.assertIsNotNone(v,reason)
        self.assertEqual(reason,"named_lemma")
        self.assertIn("Let $R$",v["hypotheses"][0])
        self.assertIn("Then",v["local_context_used"][0]["context_source_statement"])
        self.assertEqual(len(v["local_context_used"]),1)

    def test_unresolvable_source_label_stays_pending(self):
        s=(r"Assumptions and notation as in Lemma \ref{lemma-M}. "
           r"Let $I$ be an ideal. Then $D(I)$ is a module.")
        v,reason=try_secondary(mk(s),SOURCE,{})
        self.assertIsNone(v)
        self.assertIn("not available",reason)

    def test_internal_diagram_is_not_missing_prior_context(self):
        s=(r"Let $X$ be a scheme. Then the following diagram commutes "
           r"$$\xymatrix{X\ar[r]&Y}$$")
        v,reason=try_secondary(mk(s),SOURCE,{})
        self.assertIsNotNone(v,reason)
        self.assertEqual(reason,"internal_diagram")

    def test_external_situation_remains_blocked(self):
        s=r"In Situation \ref{situation-X}. Then $P$."
        v,reason=try_secondary(mk(s),SOURCE,{})
        self.assertIsNone(v)

    def test_original_statement_not_replaced(self):
        s=(r"Let $X$ be a scheme. Then $X$ is proper as in "
           r"Definition \ref{definition-proper}.")
        v,reason=try_secondary(mk(s),SOURCE,{})
        self.assertIsNotNone(v,reason)
        self.assertEqual(v["statement"],s)

if __name__=="__main__":
    unittest.main()

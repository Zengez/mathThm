"""Regression tests: Stacks theorem clauses should respect logical scope."""
from __future__ import annotations
import unittest
from scripts.stacks_section_walk_scale300_reconstruct import source_logical_shape

def parse(src):
    return source_logical_shape(src,src,
                                ["Legacy Pass 2 hypothesis"],
                                ["Legacy Pass 2 conclusion"])

class TestSourceLogicalScope(unittest.TestCase):
    def test_assume_list_is_premises_not_conclusions(self):
        src=r"""Let X be a Noetherian scheme. Assume
\begin{enumerate}
\item F is coherent.
\item G is coherent.
\end{enumerate}
Then F plus G is coherent."""
        shape,h,c,items,additional,holds=parse(src)
        self.assertEqual(shape,"listed_premises_then_conclusion")
        self.assertIn("F is coherent.",h)
        self.assertIn("G is coherent.",h)
        self.assertEqual(c,["F plus G is coherent."])
        self.assertNotIn("F is coherent.",c)
        self.assertFalse(holds)

    def test_assume_shared_existential_is_hypothesis(self):
        src=r"""Let X be a scheme. Assume there exist
\begin{enumerate}
\item a closed subset Z,
\item a closed subscheme D
\end{enumerate}
such that X = Z union D.
Then X has property P."""
        shape,h,c,items,addition,holds=parse(src)
        self.assertEqual(shape,"shared_existential_witness_hypotheses")
        self.assertEqual(c,["X has property P."])
        self.assertTrue(any("closed subset Z" in q and "closed subscheme D" in q for q in h))
        self.assertTrue(holds)

    def test_equivalent_conditions_are_not_hypotheses(self):
        src=r"""Let f:X to Y be a morphism. The following are equivalent:
\begin{enumerate}
\item f is finite.
\item f is proper with finite fibres.
\end{enumerate}"""
        shape,h,c,items,addition,holds=parse(src)
        self.assertEqual(shape,"equivalent_conditions")
        self.assertEqual(c,items)
        self.assertTrue(all(q not in h for q in items))

    def test_nested_enumeration_kept_as_whole_statement_and_held(self):
        src=r"""Let P be a property such that
\begin{enumerate}
\item there exist objects satisfying
\begin{enumerate}
\item A,
\item B.
\end{enumerate}
\item C.
\end{enumerate}
Then P holds."""
        shape,h,c,items,addition,holds=parse(src)
        self.assertEqual(shape,"nested_or_multi_enumeration_needs_review")
        self.assertEqual(c,[src])
        self.assertTrue(holds)

    def test_shared_existential_conclusion_is_not_split(self):
        src=r"""Let X be a scheme. Then there exist x and y such that
\begin{enumerate}
\item x has property A,
\item y has property B.
\end{enumerate}"""
        shape,h,c,items,addition,holds=parse(src)
        self.assertEqual(shape,"shared_existential_witness_properties")
        self.assertEqual(c,[src])
        self.assertTrue(holds)

if __name__=="__main__":
    unittest.main()

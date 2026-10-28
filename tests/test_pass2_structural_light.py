import unittest
from scripts.pass2_structural_light import split

class StructuralPass2Tests(unittest.TestCase):
    def test_explicit_then_with_enumerated_conclusions(self):
        s=r"Let $R$ be a ring. Then \begin{enumerate}\item $R$ is a ring.\end{enumerate}"
        h,c,r=split(s)
        self.assertTrue(h.startswith("Let "))
        self.assertIn(r"\item",c)
    def test_enumerated_assumptions_and_conclusions(self):
        s=r"Let $R$ be a ring. Assume \begin{enumerate}\item $R$ is Noetherian.\end{enumerate} Then $R$ is Noetherian."
        h,c,r=split(s)
        self.assertIn("Assume",h)
        self.assertIn("Noetherian",c)
    def test_equivalence_requires_semantics(self):
        s=r"Let $X$ be a space. The following are equivalent \begin{enumerate}\item $P$.\item $Q$.\end{enumerate}"
        h,c,n=split(s)
        self.assertIsNone(h)
        self.assertIn("equivalence",n)
    def test_inherited_context_requires_more(self):
        s=r"In Situation \ref{situation-foo} if $A$, then $B$."
        h,c,n=split(s)
        self.assertIsNone(h)
    def test_then_inside_enumerate_is_not_outer_boundary(self):
        s=r"Let $R$ be a ring. \begin{enumerate}\item If $P$, then $Q$.\end{enumerate}"
        h,c,n=split(s)
        self.assertIsNone(h)
    def test_simple_intro_and_unconditional_claim(self):
        s=r"Let $X$ be a scheme. There exists a morphism $X\to Y$."
        h,c,n=split(s)
        self.assertIn("scheme",h)
        self.assertIn("exists",c)
    def test_then_inside_math_does_not_split(self):
        s=r"Let $A$ be a ring. In $x \text{ then } y$ the expression is defined."
        h,c,n=split(s)
        self.assertIsNone(h)

if __name__=="__main__":
    unittest.main()

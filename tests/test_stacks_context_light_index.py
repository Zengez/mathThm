"""Unit safeguards for the fast Stacks opening/label index."""
import unittest
from scripts.stacks_context_light_index import scan_file, exact_label, candidate_context_bundle, LABELS, OPENINGS

SYNTHETIC=r"""
\title{Synthetic}
\section{Introduction}
\label{section-introduction}
We will work over a fixed base $S$.
\begin{lemma}
\label{lemma-a}
For all points ...
\end{lemma}
\begin{proof}
\label{lemma-proof-only}
No proof text may enter the index.
\end{proof}
\section{Second}
\label{section-second}
We use the same notation.
\subsection{Later restriction}
\label{subsection-later}
Let $S$ be Noetherian.
\begin{definition}
\label{definition-b}
...
\end{definition}
"""

class SourceIndexUnitTests(unittest.TestCase):
    def test_preamble_stops_before_formal_statement_and_subsection(self):
        q=scan_file(SYNTHETIC,"example.tex",1,"Test")
        self.assertEqual(q["sections"],2)
        self.assertEqual(q["subsections"],1)
        self.assertEqual(len(q["openings"]),2)
        self.assertIn("fixed base",q["openings"][0]["opening_preview"])
        self.assertNotIn("For all points",q["openings"][0]["opening_preview"])
        self.assertNotIn("Noetherian",q["openings"][1]["opening_preview"])
        self.assertEqual(q["openings"][1]["section_label"],"section-second")
        self.assertTrue(q["openings"][0]["is_chapter_introduction"])

    def test_exact_labels_and_no_proof_body(self):
        q=scan_file(SYNTHETIC,"example.tex",1,"Test")
        bykey={x["local"]:x for x in q["labels"]}
        self.assertIn("lemma-a",bykey)
        self.assertIn("definition-b",bykey)
        self.assertIn("section-introduction",bykey)
        self.assertNotIn("lemma-proof-only",bykey)
        self.assertEqual(bykey["lemma-a"]["full"],"example-lemma-a")
        self.assertEqual(bykey["definition-b"]["value"][-1],"subsection-later")

    def test_pinned_repository_lookup_when_built(self):
        if not LABELS.exists() or not OPENINGS.exists():
            self.skipTest("Pinned index not generated")
        global_item=candidate_context_bundle("formal-spaces.tex",500,[])
        late_item=candidate_context_bundle("formal-spaces.tex",900,[])
        tag="formal-spaces:section-conventions"
        self.assertNotIn(tag,{x["context_id"] for x in global_item["standing_convention_leads"]})
        self.assertIn(tag,{x["context_id"] for x in late_item["standing_convention_leads"]})
        self.assertEqual(exact_label("morphisms","section-closed-immersions")["status"],"resolved_exact")
        self.assertEqual(exact_label("morphisms","schemes-definition-immersion")["status"],"resolved_exact")
        self.assertEqual(exact_label("morphisms","nonexistent-reference-xyz")["status"],"unresolved")

if __name__=="__main__":
    unittest.main()

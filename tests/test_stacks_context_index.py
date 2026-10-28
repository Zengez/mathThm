"""Tests of bounded source-context indexing, safeguards and lookup semantics."""
import json
import unittest
from pathlib import Path

from scripts import harvest_pipeline as p
from scripts import stacks_context_index as atlas

class StacksContextIndexTests(unittest.TestCase):
    def setUp(self):
        if not atlas.REVIEWS.is_file() or not atlas.PACKETS.is_file():
            self.skipTest("Pinned Stacks source-context snapshots absent")

    def test_review_coverage_and_nonrecursive_links(self):
        reviews=p.load_rows(atlas.REVIEWS,"context_id")
        packets=p.load_rows(atlas.PACKETS,"context_id")
        self.assertEqual(len(reviews),55)
        self.assertEqual(set(reviews),set(packets))
        self.assertEqual(len({x["source_url"] for x in reviews.values()}),55)
        self.assertTrue(all(not x.get("hypotheses_already_modified",False) for x in reviews.values()))
        self.assertEqual(reviews["formal-spaces:section-conventions"]["scope"],"from_here_only")
        self.assertEqual(reviews["etale:section-conventions"]["candidate_action"],"never_auto_add")
        self.assertEqual(reviews["desirables:section-conventions"]["scope"],"not_applicable")
        self.assertIn("stacks-properties:section-conventions",
                      reviews["stacks-morphisms:section-conventions"]["inherit_from"])

    def test_chapter_lookup_scope_preserved(self):
        if not atlas.LOOKUP.is_file() or not atlas.ATLAS.is_file():
            self.skipTest("Build atlas first")
        lookup=json.loads(atlas.LOOKUP.read_text())
        self.assertEqual(len(lookup["chapter_contexts"]),115)
        self.assertTrue(lookup["no_auto_hypothesis_expansion"])
        self.assertTrue(lookup["no_inherited_assumptions_auto_propagated"])
        pre=atlas.get_candidate_context_leads("formal-spaces.tex",statement_line=500)
        post=atlas.get_candidate_context_leads("formal-spaces.tex",statement_line=900)
        key="formal-spaces:section-conventions"
        self.assertNotIn(key,{x["context_id"] for x in pre["context_leads"]})
        self.assertIn(key,{x["context_id"] for x in post["context_leads"]})
        self.assertNotIn("desirables:section-conventions",
                         {x["context_id"] for x in atlas.get_candidate_context_leads(
                             "desirables.tex",statement_line=120)["context_leads"]})
        related=atlas.get_candidate_context_leads("stacks-morphisms.tex",statement_line=1000)
        self.assertTrue(any("stacks-properties:section-conventions" in x["inherit_context_ids"]
                            for x in related["context_leads"]))
        common=atlas.get_candidate_context_leads("morphisms.tex",statement_line=1000)
        self.assertIn("conventions:section-algebra",
                      {x["context_id"] for x in common["context_leads"]})
        self.assertNotIn("conventions:section-comments",
                         {x["context_id"] for x in common["context_leads"]})

if __name__=="__main__":
    unittest.main()

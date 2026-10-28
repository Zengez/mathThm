"""Regression checks for the small non-destructive standalone-context review pilot."""
import unittest
from pathlib import Path
from scripts import harvest_pipeline as p

ROOT=Path("harvest")
PACKETS=ROOT/"standalone_context_pilot_2026-10-28_packets.jsonl"
REVIEWS=ROOT/"standalone_context_pilot_2026-10-28_first_review.jsonl"

class BoundedStandaloneContextPilotTests(unittest.TestCase):
    def test_all_pilot_results_preserve_source_and_scope_uncertainty(self):
        if not PACKETS.is_file() or not REVIEWS.is_file():
            self.skipTest("Pilot artifacts not present")
        packets=p.load_rows(PACKETS,"candidate_id")
        notes=p.load_rows(REVIEWS,"candidate_id")
        self.assertEqual(len(packets),len(notes))
        self.assertEqual(len(notes),19)
        merged={i for i,x in notes.items() if x["merge_group"] is not None}
        self.assertEqual(len(merged),8)
        self.assertTrue(all(notes[i]["source_context_status"]==
                            "provisional_duplicate_context_comparison" for i in merged))
        proposed=[x for x in notes.values() if x["proposed_hypotheses"]]
        self.assertEqual(len(proposed),6)
        for ident,row in notes.items():
            original=packets[ident]
            self.assertEqual(row["source_revision"],original["source_revision"])
            self.assertEqual(row["source_file"],original["source_filename"])
            self.assertEqual(row["source_line"],original["source_statement_line"])
            self.assertTrue(row["pass2_original_untouched"])
            self.assertFalse(row["canonical_statement_published"])
            self.assertFalse(row["verified_theorem"])
            self.assertTrue(row["remaining_issues"])
            self.assertTrue(all("stacks-project/blob/a04446e57" in url
                                for url in row["source_evidence"]))
        byfile={row["source_file"]:row for row in notes.values()
                if row["merge_group"] is None}
        self.assertIn("separated",byfile["moduli.tex"]["proposed_hypotheses"][0])
        self.assertIn("finite presentation",byfile["moduli.tex"]["proposed_hypotheses"][0])
        self.assertIn("R = A",str(byfile["varieties.tex"]["proposed_hypotheses"]))
        self.assertEqual(byfile["etale.tex"]["source_context_status"],
                         "no_missing_standing_hypothesis_detected_but_two_definitions_needed")

if __name__=="__main__":
    unittest.main()

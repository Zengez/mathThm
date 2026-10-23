import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/"data/theorems.json").read_text(encoding="utf-8"))
        cls.items=cls.data["records"]

    def test_records_and_unique_ids(self):
        self.assertEqual(self.data["schema"],"maththm.theorems.v1")
        self.assertEqual(len(self.items),20)
        self.assertEqual(len({r["id"] for r in self.items}),20)
        self.assertGreaterEqual(len({r["area"] for r in self.items}),7)

    def test_minimum_proof_provenance(self):
        for record in self.items:
            with self.subTest(record=record["id"]):
                self.assertTrue(record["hypotheses"])
                self.assertTrue(record["conclusions"])
                self.assertTrue(record["statement"])
                self.assertTrue(record["source_url"].startswith("https://"))
                self.assertTrue(record["proofs"])
                self.assertEqual(record["review_status"],"cursory_screened_unverified")
                self.assertTrue(record["statement_editorial"])
                for proof in record["proofs"]:
                    self.assertTrue(proof["url"].startswith("https://"))
                    self.assertTrue(proof["locator"])
                    self.assertEqual(proof["screening"],"cursory_screened")

    def test_side_specific_tags_and_equivalence(self):
        for r in self.items:
            self.assertIsInstance(r["hypothesis_tags"],list)
            self.assertIsInstance(r["conclusion_tags"],list)
        hb=next(x for x in self.items if x["id"]=="thm.topology.heine-borel")
        self.assertEqual(len(hb["equivalence_sides"]),2)

if __name__=="__main__":
    unittest.main()

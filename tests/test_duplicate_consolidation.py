"""Regression coverage for conservative duplicate merge and source/proof retention."""
import json
import unittest
from pathlib import Path

from scripts import candidate_consolidation as c
from scripts import harvest_pipeline as p
from scripts.theorem_schema import validate

class DuplicateConsolidationTests(unittest.TestCase):
    def test_every_flagged_group_has_an_explicit_adjudication_path(self):
        if not c.POLICY.is_file() or not c.REVIEW.is_file():
            self.skipTest("Real Stacks duplicate snapshot is not part of this checkout")
        policy=json.loads(c.POLICY.read_text())
        reviewed=p.read_jsonl(c.REVIEW)
        selected={r["group_number"] for r in policy["approved_merge_groups"]}
        self.assertEqual(len(reviewed),102)
        self.assertEqual(len(selected),8)
        self.assertNotIn(82,selected)  # topology-sensitive fppf/ph convention
        self.assertNotIn(97,selected)  # scheme vs algebraic space setting
        for row in reviewed:
            self.assertTrue(row["records"])
            self.assertEqual(row["size"],len(row["records"]))
            if row["group_number"] in selected:
                self.assertTrue(row["same_raw_source_text"])
                self.assertTrue(row["same_hypothesis_conclusion"])
                self.assertFalse(row["same_source_url"])
                self.assertFalse(row["same_proof_url"])
        self.assertTrue(policy["no_proofs_screened"])

    def test_provisionally_accepted_merge_keeps_other_proofs_uninspected(self):
        ident="candidate.stacks.primary"
        source={
            "name":"Stacks Project","attribution":"Stacks Project",
            "license_note":"Public pinned LaTeX source",
            "revision":"a"*40,
            "label":"lemma-A",
            "statement_locator":"a.tex:1",
            "source_url":"https://example.org/a.tex#L1",
            "proof_url":"https://example.org/a.tex#L2",
            "proof_locator":"a.tex:2",
            "confidence":"high",
        }
        raw={"candidate_id":ident,"entry_type":"lemma","batch_id":"demo",
             "collected_on":"2026-10-28","source":source}
        structured={
            "context_status":"resolved","result_classification":"mathematical_result",
            "statement":"If A, then B.","hypotheses":["A"],"conclusions":["B"],
            "hypothesis_tags":[],"conclusion_tags":[],"area":"Algebra",
            "title":"Demo","statement_editorial_notes":"",
        }
        checked={"outcome":"plausible","scan_completed":True,
                 "proof_checked_on":"2026-10-28","reason":"Fixture, not an actual review"}
        merge={
            "canonical_candidate_id":ident,
            "member_candidate_ids":[ident,"candidate.stacks.alias"],
            "source_references":[
                {"candidate_id":ident,"source_url":source["source_url"]},
                {"candidate_id":"candidate.stacks.alias",
                 "source_url":"https://example.org/other.tex#L1"},
            ],
            "proof_references":[
                {"candidate_id":ident,"proof_url":source["proof_url"],"proof_locator":"a.tex:2"},
                {"candidate_id":"candidate.stacks.alias",
                 "proof_url":"https://example.org/other.tex#L2",
                 "proof_locator":"other.tex:2"},
            ],
        }
        result=p.provisional_record(raw,structured,checked,merged=merge)
        self.assertEqual(result["merged_candidate_ids"],merge["member_candidate_ids"])
        self.assertEqual(len(result["proofs"]),1)
        self.assertEqual(result["proofs"][0]["screening"],"cursory_screened")
        self.assertEqual(len(result["proof_candidates"]),1)
        self.assertEqual(result["proof_candidates"][0]["status"],"uninspected")
        self.assertEqual(result["proof_candidates"][0]["url"],
                         "https://example.org/other.tex#L2")
        self.assertEqual(result["source_references"],merge["source_references"])
        corpus={"schema":"maththm.theorems.v1","contract_revision":2,
                "records":[result],"total":1}
        self.assertEqual(validate(corpus)["records"],1)
        with self.assertRaisesRegex(ValueError,"Only a canonical candidate"):
            other={**raw,"candidate_id":"candidate.stacks.alias"}
            p.provisional_record(other,structured,checked,merged=merge)

if __name__=="__main__":
    unittest.main()

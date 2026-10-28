"""Structural accepted-record regressions; these DO NOT review mathematics."""
import copy
import json
import unittest
from pathlib import Path

from scripts.theorem_schema import load_validate, validate

ROOT=Path(__file__).resolve().parent.parent

class RecordSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/"data/theorems.json").read_text(encoding="utf-8"))

    def mutate(self, transform, message):
        bad=copy.deepcopy(self.data)
        transform(bad["records"][0])
        with self.assertRaisesRegex(ValueError,message):
            validate(bad)

    def test_existing_catalog_revision_and_provenance_valid(self):
        summary=load_validate(ROOT/"data/theorems.json")
        self.assertEqual(summary["records"],len(self.data["records"]))
        self.assertGreaterEqual(summary["records"],20)
        self.assertEqual(self.data["contract_revision"],2)

    def test_optional_titles_are_allowed(self):
        data=copy.deepcopy(self.data)
        data["records"][0]["title"]=None
        validate(data)

    def test_missing_proof_and_unscreened_proofs_rejected(self):
        self.mutate(lambda r:r.update(proofs=[]),"requires accessible proof")
        self.mutate(lambda r:r["proofs"][0].update(screening="uninspected"),
                    "at least cursory screened")
        self.mutate(lambda r:r["proofs"][0].update(locator=""),"must be nonempty text")

    def test_unverified_statement_cannot_masquerade_as_transcription(self):
        self.mutate(lambda r:r["statement_provenance"].update(
            basis="source_transcription"),"source transcription requires preserved")
        self.mutate(lambda r:r["statement_provenance"].update(
            transcription_status="preserved",source_text=None),"nonempty text")
        self.mutate(lambda r:r["statement_provenance"].update(
            transcription_status="not_transcribed",source_text="Fabricated quote"),
            "must be null")

    def test_bad_tags_statuses_and_dates_rejected(self):
        self.mutate(lambda r:r["tag_annotations"].append({
            "side":"conclusions","tag":"not in tags","origin":"editor_approved"
        }),"annotation does not match")
        self.mutate(lambda r:r["mathematical_audit"].update(
            status="verified"),"do not label verified")
        self.mutate(lambda r:r["acquisition"].update(
            status="discovered"),"cursory proof screening")
        self.mutate(lambda r:r["proofs"][0].update(
            accessed_on="tomorrow"),"expected YYYY-MM-DD")

    def test_unique_ids_exact_counts_https_and_no_candidate_only_acceptance(self):
        data=copy.deepcopy(self.data)
        data["records"].append(copy.deepcopy(data["records"][0]))
        data["total"]=len(data["records"])
        with self.assertRaisesRegex(ValueError,"duplicate ID"):
            validate(data)
        self.mutate(lambda r:r.update(source_url="http://example.org"),"public HTTPS")
        self.mutate(lambda r:r.update(proofs=[],proof_candidates=[
            {"url":"https://example.org/maybe","status":"uninspected"}
        ]),"requires accessible proof")
        data=copy.deepcopy(self.data);data["total"]=1
        with self.assertRaisesRegex(ValueError,"must equal number"):
            validate(data)

if __name__=="__main__":
    unittest.main()

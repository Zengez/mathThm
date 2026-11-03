"""Small regression suite for the one-time master migration contract."""
import unittest

from scripts.migrate_phase2_master import (
    SOURCE_REV, SCHEMA, archived_snapshot, canonical, content_digest,
    sha256, validate_records,
)


class CanonicalMasterTests(unittest.TestCase):
    def base_row(self, *, held=False):
        form = {
            "statement": "If P then Q.",
            "hypotheses": ["P"],
            "conclusions": ["Q"],
            "logical_form": "single_implication",
            "structured_cases": None,
            "equivalence_sides": None,
        }
        row = {
            "candidate_id": "candidate.stacks.synthetic",
            "source_revision": SOURCE_REV,
            "source_file": "algebra.tex",
            "source_line": 120,
            "source_label": "lemma-synthetic",
            "original_source_statement_tex": "Let P hold. Then Q.",
            "decision": "source_equivalence_held" if held else "source_equivalence_approved",
            "reviewer": "phase2-independent-worker",
            "source_first_review": True,
            "proof_reviewed": False,
            "prior_stage_a_reviewer": "stage-a",
            "prior_stage_b_reviewer": "stage-b",
            "semantic_review_note": "Independently compared exact pinned hypotheses and conclusion.",
            "referenced_immutable_inputs": {
                "stage_a_artifact": "harvest/a.jsonl",
                "stage_a_blob_sha": "a" * 40,
                "stage_b_file": "work/b.jsonl",
                "stage_b_blob_sha": "b" * 40,
                "phase3_review_file": "work/c.jsonl",
                "phase3_review_blob_sha": "c" * 40,
                "phase2_proposal_file": "work/d.jsonl",
                "phase2_proposal_blob_sha": "d" * 40,
            },
        }
        if held:
            row.update(hold_reason="Missing I", hold_classification="missing_context",
                       proposed_correction="Introduce the index set I explicitly.")
        else:
            row["final_content"] = form
            row["approved_content_sha256"] = content_digest(
                row["candidate_id"], SOURCE_REV, form)
        return row

    def test_nested_form_normalization(self):
        source = self.base_row()
        snap = archived_snapshot("final_worker", "worker2.jsonl", source, 1)
        proof = {
            "outcome": "plausible",
            "scan_completed": True,
            "proof_checked_on": "2026-11-01",
            "stage_b_reviewed_content_sha256_unregistered": source["approved_content_sha256"],
        }
        obj = canonical(source["candidate_id"], source,
                        origin="final_worker", worker=2,
                        phase3=proof, snapshots=[snap])
        self.assertEqual(obj["schema"], SCHEMA)
        self.assertEqual(obj["formulation"]["statement"], "If P then Q.")
        self.assertEqual(obj["provenance"]["stage_a_artifact"], "harvest/a.jsonl")
        self.assertEqual(obj["provenance"]["stage_b_blob_sha"], "b" * 40)
        self.assertEqual(obj["audit"]["migration_flags"], [])
        self.assertEqual(validate_records([obj]), [])

    def test_hold_remains_unregistered(self):
        source = self.base_row(held=True)
        obj = canonical(source["candidate_id"], source, origin="final_worker",
                        phase3={"outcome": "plausible"})
        self.assertEqual(obj["phase2"]["decision"], "source_equivalence_held")
        self.assertIsNone(obj["formulation"]["approved_content_sha256"])
        self.assertFalse(obj["publication"]["publication_ready"])
        self.assertFalse(obj["publication"]["phase2_registered"])

    def test_historical_authority_preserved(self):
        row = self.base_row()
        row.update(row["final_content"])
        del row["final_content"]
        row["phase2_validated"] = True
        row["phase3_eligible"] = True
        row["mathematical_approval_origin"] = "documented historical source-first review"
        obj = canonical(row["candidate_id"], row, origin="historical_authoritative")
        self.assertTrue(obj["phase2"]["authoritative_registered"])
        self.assertTrue(obj["publication"]["phase3_eligible"])
        self.assertFalse(obj["publication"]["published"])
        self.assertEqual(obj["audit"]["migration_flags"], [])

    def test_archival_snapshot_is_information_preserving(self):
        row = self.base_row()
        snap = archived_snapshot("final_worker", "worker2.jsonl", row, 1)
        import json
        self.assertEqual(json.loads(snap["original_record_json"]), row)
        self.assertEqual(sha256(snap["original_record_json"]),
                         snap["content_sha256"])


if __name__ == "__main__":
    unittest.main()

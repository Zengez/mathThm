"""Metadata-only canonical coordinator regression tests (no legacy worker input)."""
from copy import deepcopy
import hashlib
import unittest
from unittest.mock import patch

from scripts import reconcile_phase2_master as reconciler
from scripts.migrate_phase2_master import SOURCE_REV, SCHEMA, content_digest


class ReconciliationTests(unittest.TestCase):
    CID = "candidate.stacks.synthetic"

    def fixtures(self):
        form = {
            "statement": "If P then Q.",
            "hypotheses": ["P"], "conclusions": ["Q"],
            "logical_form": "single_implication", "structured_cases": None,
            "equivalence_sides": None,
            "approved_content_sha256": "stale-unregistered-fingerprint",
        }
        row = {
            "schema": SCHEMA, "candidate_id": self.CID,
            "source": {"revision": SOURCE_REV, "original_statement_tex": "Let P. Then Q.",
                       "original_statement_sha256": "legacy-sha"},
            "formulation": form,
            "phase2": {"decision": "source_equivalence_approved", "reviewer": "original"},
            "phase3": {"reviewed_content_sha256_raw": "legacy-phase3-fingerprint",
                       "reviewed_content_digest_compatible": False},
            "provenance": {"stage_b_blob_sha": "a" * 40},
            "publication": {"phase2_registered": False, "phase3_eligible": False,
                            "publication_ready": False, "published": False},
            "audit": {"migration_flags": ["approved_formulation_digest_mismatch"],
                      "lossless_normalizations": [], "record_snapshots": []},
        }
        held = deepcopy(row)
        held["candidate_id"] = "candidate.stacks.zzz"
        held["phase2"]["decision"] = "source_equivalence_held"
        held["formulation"]["approved_content_sha256"] = None
        held["audit"]["migration_flags"] = []
        sha = content_digest(self.CID, SOURCE_REV, form)
        source_sha = hashlib.sha256(row["source"]["original_statement_tex"].encode()).hexdigest()
        res = {
            "schema": reconciler.RESOLUTION_SCHEMA, "candidate_id": self.CID,
            "worker": 1, "source_revision": SOURCE_REV,
            "original_issue_types": ["approved_formulation_digest_mismatch"],
            "resolution": "mechanical_fix_verified", "content_unchanged": True,
            "verified_approved_content_sha256": sha,
            "verified_source_statement_sha256": source_sha,
            "verified_phase3_content_sha256": sha,
            "evidence_files": ["immutable-source"], "audit_note": "No reviewed content changed.",
        }
        return [row, held], {self.CID: res}

    def test_metadata_only_idempotent(self):
        records, decisions = self.fixtures()
        prior = deepcopy(records)
        with patch.object(reconciler, "EXPECTED_MASTER", 2), \
             patch.object(reconciler, "EXPECTED_APPROVED", 1), \
             patch.object(reconciler, "EXPECTED_HELD", 1):
            reconciler.reconcile(records, decisions)
            self.assertEqual(records[0]["formulation"]["statement"], prior[0]["formulation"]["statement"])
            self.assertEqual(records[0]["phase2"], prior[0]["phase2"])
            self.assertEqual(records[0]["publication"], prior[0]["publication"])
            self.assertEqual(records[0]["phase3"]["reviewed_content_sha256_raw"],
                             prior[0]["phase3"]["reviewed_content_sha256_raw"])
            self.assertEqual(records[0]["audit"]["legacy_digest_values"]["approved_content_sha256"],
                             "stale-unregistered-fingerprint")
            once = deepcopy(records)
            reconciler.reconcile(records, decisions)
            self.assertEqual(records, once)

    def test_reject_unverified_content_identity(self):
        records, decisions = self.fixtures()
        decisions[self.CID]["verified_approved_content_sha256"] = "0" * 64
        with patch.object(reconciler, "EXPECTED_MASTER", 2), \
             patch.object(reconciler, "EXPECTED_APPROVED", 1), \
             patch.object(reconciler, "EXPECTED_HELD", 1):
            with self.assertRaisesRegex(ValueError, "does not match verified digest"):
                reconciler.reconcile(records, decisions)

    def test_reject_new_publication_authority(self):
        records, decisions = self.fixtures()
        records[0]["publication"]["publication_ready"] = True
        with patch.object(reconciler, "EXPECTED_MASTER", 2), \
             patch.object(reconciler, "EXPECTED_APPROVED", 1), \
             patch.object(reconciler, "EXPECTED_HELD", 1):
            with self.assertRaisesRegex(ValueError, "Publication authority changed|Premature publication"):
                reconciler.reconcile(records, decisions)


if __name__ == "__main__":
    unittest.main()

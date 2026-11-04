"""Offline tests for exactly scoped one-time Wikipedia 429 retry."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.retry_wikipedia_inconclusive import (
    run, read_jsonl, rate_limited, PASS, NO_PROOF, INCONCLUSIVE, SKIPPED,
)


def make_fixtures(root):
    original = Path(root) / "original.jsonl"
    prepared = Path(root) / "prepared.jsonl"
    old, prep = [], []
    for i in range(984):
        cid = f"candidate.wikipedia.test{i:04d}"
        url = f"https://en.wikipedia.org/wiki/Test_{i:04d}"
        status = PASS if i < 706 else NO_PROOF if i < 760 else INCONCLUSIVE
        old.append({"candidate_id": cid, "url": url, "input_index": i,
                    "status": status, "reason": "page_or_section_fetch_failure"})
        prep.append({"candidate_id": cid, "url": url, "input_index": i,
                     "title": f"Test {i}", "statement": "Assume A. Then B.",
                     "hypotheses": ["A"], "conclusions": ["B"],
                     "status": "standalone_prepared"})
    original.write_text("".join(json.dumps(r)+"\n" for r in old))
    prepared.write_text("".join(json.dumps(r)+"\n" for r in prep))
    return original, prepared


def result_for(candidate, status, reason="page_or_section_fetch_failure", notes=None):
    return {
        "candidate_id": candidate["candidate_id"],
        "url": candidate["url"], "input_index": candidate["input_index"],
        "status": status, "reason": reason, "proof_url": (
            candidate["url"]+"#Proof" if status == PASS else None),
        "proof_heading": "Proof" if status == PASS else None,
        "inspection_date": "2026-11-04",
        "screening_scope": "structure_only_not_validity_or_completeness",
        "fetch_notes": notes or [],
    }


class WikipediaOneTimeRetryTests(unittest.TestCase):
    def test_429_guard_and_exact_accounting(self):
        with TemporaryDirectory() as directory:
            original, prepared = make_fixtures(directory)
            calls = []
            def blocked(candidate):
                calls.append(candidate["candidate_id"])
                return result_for(candidate, INCONCLUSIVE,
                                  notes=["HTTPError: HTTP Error 429: Too Many Requests"])
            report = run(original, prepared, Path(directory)/"out",
                         delay=0, stop_after_429=4, screener=blocked, sleeper=lambda t: None)
            self.assertEqual(len(calls), 4)
            self.assertEqual(report["retry_attempted"], 4)
            self.assertEqual(report["retry_skipped_due_to_rate_limit"], 220)
            self.assertTrue(report["rate_limit_stop_triggered"])
            self.assertEqual(len(read_jsonl(Path(directory)/"out"/"retry_decisions.jsonl")),224)
            self.assertEqual(report["updated_total_inconclusive_or_deferred"],224)
            self.assertEqual(report["updated_total_screened"],706)

    def test_successes_stay_distinct_from_nonpasses(self):
        with TemporaryDirectory() as directory:
            original, prepared = make_fixtures(directory)
            def mix(candidate):
                i = candidate["input_index"]
                if i == 760:
                    return result_for(candidate,PASS,"argument_like_prose")
                if i == 761:
                    return result_for(candidate,NO_PROOF,"no_proof_labeled_section")
                return result_for(candidate,INCONCLUSIVE,
                                  notes=["HTTPError: HTTP Error 429: Too Many Requests"])
            report = run(original, prepared, Path(directory)/"out",
                         delay=0, stop_after_429=4, screener=mix, sleeper=lambda t: None)
            self.assertEqual(report["retry_proof_looking_content_found"],1)
            self.assertEqual(report["retry_no_visible_proof"],1)
            self.assertEqual(report["retry_still_inconclusive_attempted"],4)
            self.assertEqual(report["retry_skipped_due_to_rate_limit"],218)
            self.assertEqual(report["updated_total_screened"],707)
            self.assertEqual(report["updated_total_no_visible_proof"],55)
            self.assertEqual(len(read_jsonl(Path(directory)/"out"/"newly_screened_candidates.jsonl")),1)
            self.assertEqual(len(read_jsonl(Path(directory)/"out"/"newly_no_visible_proof.jsonl")),1)

    def test_rate_limit_classification(self):
        self.assertTrue(rate_limited({"status":INCONCLUSIVE,
                                     "fetch_notes":["HTTPError: HTTP Error 429: Too Many Requests"]}))
        self.assertFalse(rate_limited({"status":NO_PROOF,
                                      "fetch_notes":["HTTPError: HTTP Error 429"]}))
        self.assertFalse(rate_limited({"status":INCONCLUSIVE,
                                      "fetch_notes":["HTTPError: HTTP Error 404"]}))


if __name__ == "__main__":
    unittest.main()

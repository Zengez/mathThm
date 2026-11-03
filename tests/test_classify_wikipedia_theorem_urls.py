"""Tests for conservative Wikipedia mathematical theorem classification (offline)."""
import json
import tempfile
from pathlib import Path
import unittest

from scripts.classify_wikipedia_theorem_urls import (
    classify, export_results, fetch_metadata, read_urls, title_from_url
)


class FakeClient:
    def __init__(self):
        self.calls = 0

    def query(self, **kwargs):
        self.calls += 1
        if not kwargs.get("clcontinue"):
            return {
                "query": {
                    "redirects": [{"from": "Math theorem redirect", "to": "Math theorem"}],
                    "pages": [
                        {"title": "Math theorem", "categories": [
                            {"title": "Category:Theorems in real analysis"}],
                         "extract": "In mathematics, this theorem establishes a fact."},
                        {"title": "1985 election", "categories": [
                            {"title": "Category:1985 elections"}],
                         "extract": "The 1985 election was a political event."}
                    ]
                },
                "continue": {"continue": "||", "clcontinue": "token"}
            }
        return {
            "query": {"pages": [
                {"title": "Math theorem", "categories": [
                    {"title": "Category:Mathematical theorems"}]}
            ]}
        }


class ClassifierTests(unittest.TestCase):
    def test_high_precision_acceptance_and_review(self):
        self.assertEqual(classify(
            "Heine–Borel theorem", ["Compactness theorems"], "")[0], "accepted")
        self.assertEqual(classify(
            "Alternating series test", ["Mathematical convergence"],
            "The test is an important mathematical theorem.")[0], "accepted")
        self.assertEqual(classify(
            "1985 election", ["1985 elections"],
            "The election was a political event.")[0], "rejected")
        self.assertEqual(classify(
            "Alexander's trick", ["Topology"],
            "A construction in topology.")[0], "needs_review")
        self.assertEqual(classify(
            "Abc conjecture", ["Number theory"],
            "The conjecture remains open.")[0], "needs_review")
        self.assertEqual(classify(
            "Theorem of fiction", ["Novels"], "A novel.")[0], "needs_review")
        self.assertEqual(classify(
            "No longer here", [], "", missing=True)[0], "needs_review")
        self.assertEqual(classify(
            "ACL2", ["Automated theorem proving", "Proof assistants"],
            "ACL2 is an automated theorem prover.")[0], "needs_review")
        self.assertEqual(classify(
            "Proof of Bertrand's postulate", ["Proofs of theorems", "Number theory"],
            "This page describes a proof.")[0], "needs_review")
        self.assertEqual(classify(
            "List of long mathematical proofs", ["Mathematical theorems"],
            "A list of proofs.")[0], "needs_review")
        self.assertEqual(classify(
            "Proof assistant", ["Theorems in logic"], "Software")[0], "needs_review")
        self.assertEqual(classify(
            "Hex (board game)", ["Theorems in topology", "Board games"],
            "Hex is a two-player abstract strategy board game.")[0], "needs_review")
        self.assertEqual(classify(
            "William of Soissons", ["Theorems in propositional logic"],
            "William of Soissons was a French logician.")[0], "needs_review")
        self.assertEqual(classify(
            "Tits alternative", ["Theorems in group theory"],
            "In mathematics, the Tits alternative is an important theorem.")[0], "accepted")


    def test_url_validation_and_pagination(self):
        url = "https://en.wikipedia.org/wiki/Math_theorem_redirect"
        self.assertEqual(title_from_url(url), "Math theorem redirect")
        with self.assertRaises(ValueError):
            title_from_url("https://example.com/wiki/Other")
        c = FakeClient()
        rows = fetch_metadata(c, [(url, "Math theorem redirect"),
                                  ("https://en.wikipedia.org/wiki/1985_election", "1985 election")])
        self.assertEqual(c.calls, 2)
        self.assertEqual(rows[0]["resolved_title"], "Math theorem")
        self.assertEqual(len(rows[0]["categories"]), 2)
        self.assertEqual(rows[1]["resolved_title"], "1985 election")

    def test_export_preserves_every_url(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rows = [
                {"url": "https://en.wikipedia.org/wiki/Heine-Borel_theorem",
                 "title": "Heine-Borel theorem", "resolved_title": "Heine-Borel theorem",
                 "intro": "", "categories": ["Theorems in real analysis"], "missing": False},
                {"url": "https://en.wikipedia.org/wiki/1985_election",
                 "title": "1985 election", "resolved_title": "1985 election",
                 "intro": "", "categories": ["1985 elections"], "missing": False},
                {"url": "https://en.wikipedia.org/wiki/Alexander%27s_trick",
                 "title": "Alexander's trick", "resolved_title": "Alexander's trick",
                 "intro": "", "categories": ["Topology"], "missing": False},
            ]
            counts = export_results(root, rows, 3)
            self.assertEqual((counts["accepted"], counts["rejected"],
                              counts["needs_review"]), (1, 1, 1))
            decisions = [json.loads(x) for x in
                         (root / "decisions.jsonl").read_text().splitlines()]
            self.assertEqual(len(decisions), 3)
            self.assertTrue(all("reason" in x for x in decisions))
            self.assertEqual(len(list(root.glob("review_worker_*.jsonl"))), 4)
            self.assertEqual(read_urls(root / "accepted_urls.txt"), [rows[0]["url"]])


if __name__ == "__main__":
    unittest.main()

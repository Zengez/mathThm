"""Offline contract tests for the Wikipedia URL harvester; no live API requests."""
import tempfile
import unittest
from pathlib import Path

from scripts.wikipedia_proof_urls import (
    Store, canonical_url, category_title, check_one, crawl_category,
    proof_heading, toc_has_proof, wikitext_has_proof,
)


class FakeAPI:
    def __init__(self):
        self.calls = []

    def query(self, **kwargs):
        self.calls.append(kwargs)
        if kwargs.get("prop") == "categories":
            return {"query": {"pages": [{"categories": [
                {"ns": 14, "title": "Category:General topology"},
                {"ns": 14, "title": "Category:Wikipedia maintenance"}]}]}}
        if kwargs.get("list") == "categorymembers":
            if not kwargs.get("cmcontinue"):
                return {"query": {"categorymembers": [
                    {"ns": 0, "pageid": 123, "title": "Heine–Borel theorem"},
                    {"ns": 14, "pageid": 456, "title": "Category:Compactness theorems"},
                    {"ns": 1, "pageid": 789, "title": "Talk:Ignored"}]},
                    "continue": {"continue": "-||", "cmcontinue": "NEXT"}}
            return {"query": {"categorymembers": [
                {"ns": 0, "pageid": 123, "title": "Heine–Borel theorem"},
                {"ns": 0, "pageid": 124, "title": "Other theorem"}]}}
        if kwargs.get("action") == "parse":
            return {"parse": {
                "title": "Heine–Borel theorem" if kwargs["pageid"] == 123 else "Other theorem",
                "tocdata": {"sections": [
                    {"line": "History"},
                    {"line": "Proof without Choice" if kwargs["pageid"] == 123 else "References"}]}}}
        raise AssertionError(kwargs)


class HarvestTests(unittest.TestCase):
    def test_heading_detection(self):
        for heading in ("Proof", "Proofs", "Proof without Choice", "Alternative proof",
                        "<b>Proof</b> of theorem", "Sketch of proof"):
            self.assertTrue(proof_heading(heading))
        for heading in ("Disproof", "Proofreading", "History", "Proofer"):
            self.assertFalse(proof_heading(heading))
        self.assertTrue(toc_has_proof({"sections": [{"line": "Proof 2"}]}))
        self.assertFalse(toc_has_proof({"sections": [{"line": "References"}]}))
        self.assertTrue(wikitext_has_proof("== Overview ==\n=== Proof of the theorem ===\nbody"))
        self.assertFalse(wikitext_has_proof("Proof\n== See also =="))

    def test_url_encoding(self):
        self.assertEqual(canonical_url("Heine–Borel theorem"),
                         "https://en.wikipedia.org/wiki/Heine%E2%80%93Borel_theorem")
        self.assertEqual(category_title("Category:Real_analysis"), "Category:Real analysis")

    def test_checkpoint_pagination_resume_and_export(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "state.sqlite3"
            outfile = Path(folder) / "urls.txt"
            api = FakeAPI()
            store = Store(db)
            store.seed(["Category:Theorems in real analysis"])
            self.assertTrue(crawl_category(store, api, max_depth=4))
            self.assertEqual(store.counts()["pages_discovered"], 1)
            self.assertEqual(store.category()[2], "NEXT")
            store.db.close()
            store = Store(db)
            self.assertTrue(crawl_category(store, api, max_depth=4))
            self.assertEqual(store.counts()["pages_discovered"], 2)
            self.assertEqual(store.counts()["categories"], 3)
            self.assertTrue(check_one(store, api))
            self.assertTrue(check_one(store, api))
            self.assertFalse(check_one(store, api))
            self.assertEqual(store.counts()["matched"], 1)
            self.assertEqual(store.export(outfile), 1)
            self.assertEqual(outfile.read_text().strip(),
                             "https://en.wikipedia.org/wiki/Heine%E2%80%93Borel_theorem")
            store.db.close()


if __name__ == "__main__":
    unittest.main()

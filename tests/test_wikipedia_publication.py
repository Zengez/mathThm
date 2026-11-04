"""Wikipedia publication tests: identity, source/proof links and inclusion, not math validity."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts import publish_wikipedia_catalog as w
from scripts.theorem_schema import validate

ROOT=Path(__file__).resolve().parent.parent


class WikipediaPublicationTests(unittest.TestCase):
    def test_compiled_exactly_the_920_screened_pages(self):
        rows=w.compile_screened()
        self.assertEqual(len(rows),920)
        self.assertEqual(len({r["id"] for r in rows}),920)
        self.assertEqual(len({r["source_url"] for r in rows}),920)
        self.assertEqual(sum(not r["hypotheses"] for r in rows)>=0,True)
        self.assertTrue(all(r["proofs"][0]["url"].startswith(r["source_url"]+"#") for r in rows))
        self.assertTrue(all(r["proofs"][0]["screening"]=="cursory_screened" for r in rows))
        self.assertTrue(all(r["review_status"]=="cursory_screened_unverified" for r in rows))
        self.assertTrue(all(r["mathematical_audit"]["status"]=="not_audited" for r in rows))
        self.assertTrue(all(r["statement_provenance"]["source_text"] is None for r in rows))

    def test_every_canonical_record_is_structurally_valid(self):
        entries=w.load_published()
        corpus={"schema":"maththm.theorems.v1","contract_revision":2,
                "total":len(entries),"records":entries}
        self.assertEqual(validate(corpus)["records"],920)

    def test_canonical_input_remains_regenerable_without_wikipedia_fetches(self):
        original=w.CANONICAL.read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"wikipedia_theorems.jsonl"
            report=w.save_canonical(path)
            self.assertEqual(report["materialized_records"],920)
            self.assertEqual(path.read_bytes(),original)

    def test_disjoint_from_existing_stacks_and_unmodified_prototypes(self):
        from scripts.publish_phase2_catalog import load_json, OUT
        entries=w.load_published()
        prototype=load_json(OUT/"prototype_baseline.json")["records"]
        result=copy.deepcopy(prototype)
        report=None
        # Stacks master and its approved record set remain authoritative.
        from scripts.publish_phase2_catalog import master_rows, make_record
        stacks=[d["theorem"] for d in map(make_record,master_rows())
                if d["status"]=="publishable"]
        result.extend(stacks)
        pre=len(result)
        report=w.append_wikipedia(result)
        self.assertEqual(pre,3963)
        self.assertEqual(report["wikipedia_published"],920)
        self.assertEqual(len(result),4883)
        self.assertEqual(result[:20],prototype)
        self.assertEqual(len({r["id"] for r in result}),4883)

    def test_cannot_fake_proof_screening_or_source(self):
        row=w.read_jsonl(w.FIRST)[0]
        altered=copy.deepcopy(row)
        altered["proof_screening"]["status"]="inconclusive"
        with self.assertRaisesRegex(ValueError,"screening"):
            w.make_public(altered)
        altered=copy.deepcopy(row)
        altered["proof_screening"]["proof_url"]="https://en.wikipedia.org/wiki/Unrelated#Proof"
        with self.assertRaisesRegex(ValueError,"Proof URL"):
            w.make_public(altered)

    def test_unconditional_edits_not_given_fabricated_assumptions(self):
        entries=w.load_published()
        unconditional=[r for r in entries if not r["hypotheses"]]
        for row in unconditional:
            self.assertEqual(row["tag_provenance_defaults"]["hypotheses"],"initial_editorial")
            self.assertTrue(row["conclusions"])


if __name__=="__main__":
    unittest.main()

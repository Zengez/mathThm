"""Offline tests for GitHub Actions' split Wikipedia dump harvester."""
import bz2
import io
import tempfile
import unittest
from pathlib import Path

from scripts.wikipedia_dump_actions import (
    article_url, manifest_files, parse_dump, proof_heading, rebuild_outputs,
)

EXAMPLE_INDEX = """<html><body>Dump complete
<a href="enwiki-20261001-pages-articles-multistream2.xml-p51p90.bz2">2</a>
<a href="enwiki-20261001-pages-articles-multistream1.xml-p1p50.bz2">1</a>
<a href="enwiki-20261001-pages-articles-multistream-index1.txt-p1p50.bz2">index</a>
<a href="enwiki-20261001-pages-articles-multistream.xml.bz2">whole</a>
</body></html>"""

XML = """<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/">
<page><title>Heine–Borel theorem</title><ns>0</ns><id>1</id><revision><id>101</id><text>== History ==
== Proof without Choice ==
We omit.</text></revision></page>
<page><title>Article</title><ns>0</ns><id>2</id><revision><id>102</id><text>Some inline proof.
== References ==</text></revision></page>
<page><title>Category:Proof</title><ns>14</ns><id>3</id><revision><id>103</id><text>== Proof ==</text></revision></page>
</mediawiki>"""


class DumpTests(unittest.TestCase):
    def test_manifest_only_dated_chunks(self):
        self.assertEqual(manifest_files(EXAMPLE_INDEX, "20261001"), [
            "enwiki-20261001-pages-articles-multistream1.xml-p1p50.bz2",
            "enwiki-20261001-pages-articles-multistream2.xml-p51p90.bz2",
        ])
        with self.assertRaises(ValueError):
            manifest_files(EXAMPLE_INDEX.replace("Dump complete", "Still running"), "20261001")

    def test_scan_headings_and_namespace(self):
        payload = bz2.compress(XML.encode("utf-8"))
        with bz2.BZ2File(io.BytesIO(payload), "rb") as stream:
            urls, count = parse_dump(stream)
        self.assertEqual(count, 2)
        self.assertEqual(urls, {"https://en.wikipedia.org/wiki/Heine%E2%80%93Borel_theorem"})
        self.assertTrue(proof_heading("== Alternative proofs =="))
        self.assertFalse(proof_heading("== Disproof =="))

    def test_checkpoint_and_deduplication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chunks = manifest_files(EXAMPLE_INDEX, "20261001")
            parts = root / "20261001" / "parts"
            parts.mkdir(parents=True)
            (parts / (chunks[0] + ".txt")).write_text(article_url("A B") + "\n")
            state = rebuild_outputs(root, "20261001", chunks)
            self.assertEqual((state["completed_chunks"], state["remaining_chunks"]), (1, 1))
            (parts / (chunks[1] + ".txt")).write_text(
                article_url("A B") + "\n" + article_url("C") + "\n"
            )
            state = rebuild_outputs(root, "20261001", chunks)
            self.assertEqual((state["completed_chunks"], state["matching_unique_urls"]), (2, 2))
            self.assertEqual(len((root / "20261001" / "wikipedia_theorem_urls.txt").read_text().splitlines()), 2)


if __name__ == "__main__":
    unittest.main()

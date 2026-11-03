#!/usr/bin/env python3
"""Resumable English Wikipedia article-dump URL harvester for GitHub Actions.

Records pages with proof/proofs section headings; does NOT validate mathematics.
"""
from __future__ import annotations

import argparse
import bz2
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import logging
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

DUMPS = "https://dumps.wikimedia.org/enwiki"
CONTACT = "https://github.com/Zengez/mathThm"
FILE_PATTERN = re.compile(
    r"enwiki-(?P<date>\d{8})-pages-articles-multistream\d+"
    r"\.xml-p(?P<first>\d+)p(?P<last>\d+)\.bz2\Z"
)
HEADING = re.compile(r"^\s*={2,6}\s*(.*?)\s*={2,6}\s*$", re.MULTILINE)
WORD_PROOF = re.compile(r"\bproofs?\b", re.IGNORECASE)


class Hrefs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


def article_url(title: str) -> str:
    return "https://en.wikipedia.org/wiki/" + urllib.parse.quote(
        title.replace(" ", "_"), safe="()/:,!'~-._"
    )


def proof_heading(wikitext: str) -> bool:
    """Only headings, not inline mentions; raw wikitext can yield false positives."""
    return any(WORD_PROOF.search(m.group(1)) for m in HEADING.finditer(wikitext))


def manifest_files(index_html: str, date: str) -> list[str]:
    """Select dated partial article dumps, not their indexes or the giant whole dump."""
    if "Dump complete" not in index_html:
        raise ValueError("The dated dump does not advertise 'Dump complete'")
    parser = Hrefs()
    parser.feed(index_html)
    files = {}
    for href in parser.hrefs:
        name = urllib.parse.unquote(urllib.parse.urlsplit(href).path.rsplit("/", 1)[-1])
        match = FILE_PATTERN.fullmatch(name)
        if match and match.group("date") == date:
            files[name] = (int(match.group("first")), int(match.group("last")))
    if not files:
        raise ValueError("No split article dump files found")
    ordered = sorted(files, key=lambda name: (files[name][0], files[name][1], name))
    for prev, cur in zip(ordered, ordered[1:]):
        if files[cur][0] <= files[prev][1]:
            raise ValueError(f"Overlapping dump chunk ranges: {prev} / {cur}")
    return ordered


def download_index(date: str) -> str:
    req = urllib.request.Request(f"{DUMPS}/{date}/", headers={
        "User-Agent": f"mathThmWikipediaDumpHarvester/1.0 ({CONTACT})",
    })
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read().decode("utf-8")


def local_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_dump(stream, *, max_articles: int = 0) -> tuple[set[str], int]:
    """Streaming parser with bounded XML memory and no saved article bodies."""
    urls = set()
    examined = 0
    events = ET.iterparse(stream, events=("start", "end"))
    _, root = next(events)
    for event, elem in events:
        if event != "end" or local_tag(elem.tag) != "page":
            continue

        def child(name):
            return next((c for c in elem if local_tag(c.tag) == name), None)

        ns, title = child("ns"), child("title")
        if ns is not None and ns.text == "0" and title is not None and title.text:
            examined += 1
            revision = child("revision")
            if revision is not None:
                body = next((e.text or "" for e in revision.iter() if local_tag(e.tag) == "text"), "")
                if proof_heading(body):
                    urls.add(article_url(title.text))
        root.clear()
        if max_articles and examined >= max_articles:
            break
    return urls, examined


def scan_remote_chunk(date: str, filename: str, *, timeout=120, attempts=3):
    if not FILE_PATTERN.fullmatch(filename) or not filename.startswith(f"enwiki-{date}-"):
        raise ValueError("Unsafe/inconsistent chunk filename")
    url = f"{DUMPS}/{date}/{filename}"
    for i in range(attempts):
        try:
            request = urllib.request.Request(url, headers={
                "User-Agent": f"mathThmWikipediaDumpHarvester/1.0 ({CONTACT})"
            })
            with urllib.request.urlopen(request, timeout=timeout) as response:
                with bz2.BZ2File(response, "rb") as stream:
                    return parse_dump(stream)
        except (urllib.error.URLError, OSError, TimeoutError, ET.ParseError) as exc:
            if i == attempts - 1:
                raise
            wait = min(120, 10 * 2 ** i)
            logging.warning("Retrying %s after %s (%ds)", filename, exc, wait)
            time.sleep(wait)
    raise AssertionError("unreachable")


def atomic_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(content, encoding="utf-8")
    os.replace(temp, path)


def rebuild_outputs(root: Path, date: str, files: list[str]):
    folder = root / date
    parts = folder / "parts"
    known = set(files)
    completed = []
    urls = set()
    for part in sorted(parts.glob("*.txt")):
        filename = part.name[:-4]
        if filename not in known:
            raise ValueError(f"Unexpected checkpoint part: {part}")
        completed.append(filename)
        urls.update(x.strip() for x in part.read_text(encoding="utf-8").splitlines() if x.strip())
    atomic_text(folder / "wikipedia_theorem_urls.txt", "".join(x + "\n" for x in sorted(urls)))
    progress = {
        "snapshot": date,
        "source": f"{DUMPS}/{date}/",
        "total_chunks": len(files),
        "completed_chunks": len(completed),
        "remaining_chunks": len(files) - len(completed),
        "matching_unique_urls": len(urls),
        "completed_filenames": completed,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "English Wikipedia ns0 wikitext proof/proofs section headings",
        "validated_theorems": 0,
    }
    previous_file = folder / "progress.json"
    if previous_file.exists():
        try:
            previous = json.loads(previous_file.read_text(encoding="utf-8"))
            stable_fields = set(progress) - {"updated_at_utc"}
            if all(previous.get(key) == progress.get(key) for key in stable_fields):
                progress["updated_at_utc"] = previous.get("updated_at_utc", progress["updated_at_utc"])
        except (ValueError, OSError):
            pass
    atomic_text(previous_file, json.dumps(progress, indent=2, ensure_ascii=False) + "\n")
    return progress


def run(args):
    date = args.snapshot
    if not re.fullmatch(r"20\d{6}", date):
        raise ValueError("Snapshot must be a pinned YYYYMMDD dump date")
    if args.max_shards < 0 or args.max_minutes < 0:
        raise ValueError("Negative shard/time limits unsupported")
    folder = args.results_dir / date
    folder.mkdir(parents=True, exist_ok=True)
    manifest_file = folder / "chunk_manifest.json"
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        if manifest.get("snapshot") != date:
            raise ValueError("Existing manifest snapshot mismatch")
        files = manifest["filenames"]
        if not files or any(not FILE_PATTERN.fullmatch(x) for x in files):
            raise ValueError("Invalid stored chunk manifest")
    else:
        files = manifest_files(download_index(date), date)
        atomic_text(manifest_file, json.dumps({"snapshot": date, "filenames": files}, indent=2) + "\n")
    progress = rebuild_outputs(args.results_dir, date, files)
    logging.info("Starting enwiki %s: %d/%d chunks, %d URLs",
                 date, progress["completed_chunks"], len(files), progress["matching_unique_urls"])
    started = time.monotonic()
    processed = 0
    complete = set(progress["completed_filenames"])
    for filename in files:
        if filename in complete:
            continue
        if args.max_shards and processed >= args.max_shards:
            break
        if args.max_minutes and time.monotonic() - started >= args.max_minutes * 60:
            break
        logging.info("Scanning %s", filename)
        urls, examined = scan_remote_chunk(date, filename)
        atomic_text(folder / "parts" / (filename + ".txt"),
                    "".join(url + "\n" for url in sorted(urls)))
        processed += 1
        progress = rebuild_outputs(args.results_dir, date, files)
        logging.info("Scanned %d articles, %d headings match; finished %d/%d chunks",
                     examined, len(urls), progress["completed_chunks"], len(files))
    final = rebuild_outputs(args.results_dir, date, files)
    report = (
        f"## English Wikipedia dump harvest — {date}\n\n"
        f"- Completed chunks: **{final['completed_chunks']} / {len(files)}**\n"
        f"- Remaining chunks: **{final['remaining_chunks']}**\n"
        f"- Distinct proof-heading URLs: **{final['matching_unique_urls']}**\n"
        f"- Processed this run: **{processed}**\n"
        f"- Mathematical validation: **none**, URL discovery only\n"
    )
    atomic_text(folder / "REPORT.md", report)
    print(report)
    if args.github_summary and os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as output:
            output.write(report + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default="20261001",
                        help="Completed immutable enwiki dump YYYYMMDD")
    parser.add_argument("--results-dir", type=Path,
                        default=Path(".harvest_runs/wikipedia_dump"))
    parser.add_argument("--max-shards", type=int, default=2)
    parser.add_argument("--max-minutes", type=int, default=250)
    parser.add_argument("--github-summary", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
    run(args)


if __name__ == "__main__":
    main()

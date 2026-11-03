#!/usr/bin/env python3
"""Discover English Wikipedia URLs with an explicit proof-related section heading.

This is a discovery filter only, not a theorem/statement/proof validator.
Uses only the Python standard library; SQLite is the authoritative checkpoint.
"""
from __future__ import annotations

import argparse
import bz2
import gzip
import html
import json
import logging
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

API = "https://en.wikipedia.org/w/api.php"
SEEDS = (
    "Category:Mathematical theorems",
    "Category:Theorems in real analysis",
    "Category:Compactness theorems",
    "Category:Algebraic theorems",
    "Category:Theorems in geometry",
    "Category:Theorems in topology",
    "Category:Theorems in number theory",
    "Category:Mathematical proofs",
)
PROOF_HEADING = re.compile(r"\bproofs?\b", re.IGNORECASE)
WIKITEXT_HEADING = re.compile(r"^={2,6}\s*(.*?)\s*={2,6}\s*$", re.MULTILINE)
HTML_TAG = re.compile(r"<[^>]+>")
PARENT_RELEVANCE = re.compile(
    r"theorem|proof|lemma|mathemat|algebra|analys|topolog|geometr|number theory|"
    r"compact|calculus|probabil|combinator|logic|set theory|functional|measure|"
    r"ring theory|group theory|category theory|graph theory|differential|"
    r"complex variable|operator theory|dynamical system|order theory|"
    r"metric space|linear space|vector space|discrete math|arithmetic",
    re.IGNORECASE,
)


def canonical_url(title: str) -> str:
    return "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe="()/:,!'~-._")


def proof_heading(text: str) -> bool:
    plain = html.unescape(HTML_TAG.sub("", text))
    return bool(PROOF_HEADING.search(plain))


def toc_has_proof(toc: object) -> bool:
    if isinstance(toc, dict):
        sections = toc.get("sections", [])
    elif isinstance(toc, list):
        sections = toc
    else:
        return False
    return any(proof_heading(str(s.get("line", ""))) for s in sections if isinstance(s, dict))


def wikitext_has_proof(text: str) -> bool:
    return any(proof_heading(match.group(1)) for match in WIKITEXT_HEADING.finditer(text))


class RequestLimit(Exception):
    """Exit the current bounded run, preserving the SQLite state."""


class MediaWiki:
    def __init__(self, contact: str, delay: float = 1.5, timeout: float = 35.0,
                 attempts: int = 7, max_requests: int = 0):
        if not contact or contact == "CHANGE_ME":
            raise ValueError("Provide --contact with a real email address or public project contact URL")
        self.agent = f"mathThmWikipediaProofHeadingHarvester/1.0 ({contact}) Python-urllib"
        self.delay, self.timeout, self.attempts = delay, timeout, attempts
        self.max_requests = max_requests
        self.requests = 0
        self.last_request = 0.0

    def query(self, **kwargs: str | int) -> dict:
        if self.max_requests and self.requests >= self.max_requests:
            raise RequestLimit()
        params = {"format": "json", "formatversion": "2", "maxlag": "5", **kwargs}
        url = API + "?" + urllib.parse.urlencode(params)
        for attempt in range(self.attempts):
            if self.max_requests and self.requests >= self.max_requests:
                raise RequestLimit()
            pause = self.delay - (time.monotonic() - self.last_request)
            if pause > 0:
                time.sleep(pause)
            self.requests += 1
            self.last_request = time.monotonic()
            req = urllib.request.Request(url, headers={"User-Agent": self.agent,
                                                       "Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    payload = json.load(response)
                if "error" in payload:
                    code = payload["error"].get("code", "")
                    if code == "maxlag":
                        raise RuntimeError("maxlag: " + str(payload["error"]))
                    raise ValueError("MediaWiki API error: " + str(payload["error"]))
                return payload
            except (urllib.error.HTTPError, urllib.error.URLError,
                    TimeoutError, ConnectionError, json.JSONDecodeError, RuntimeError) as exc:
                if isinstance(exc, urllib.error.HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                    raise
                if attempt + 1 >= self.attempts:
                    raise
                wait = min(120.0, 2.0 ** attempt + 1)
                if isinstance(exc, urllib.error.HTTPError):
                    try:
                        wait = max(wait, min(120.0, float(exc.headers.get("Retry-After", "0"))))
                    except ValueError:
                        pass
                logging.warning("API request failed (%s); retry in %.1fs", exc, wait)
                time.sleep(wait)
        raise AssertionError("unreachable")


class Store:
    def __init__(self, dbfile: Path):
        dbfile.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(dbfile))
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                title TEXT PRIMARY KEY, depth INTEGER NOT NULL, continuation TEXT,
                parents_done INTEGER NOT NULL DEFAULT 0, finished INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS pages (
                pageid INTEGER PRIMARY KEY, title TEXT NOT NULL,
                checked INTEGER NOT NULL DEFAULT 0, matched INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS idx_categories_pending ON categories(finished,depth,title);
            CREATE INDEX IF NOT EXISTS idx_pages_pending ON pages(checked,pageid);
        """)
        self.db.commit()

    def seed(self, categories: list[str]):
        with self.db:
            self.db.executemany(
                "INSERT OR IGNORE INTO categories(title,depth) VALUES (?,0)",
                [(category_title(s),) for s in categories])

    def add_pages(self, pages: list[tuple[int, str]]):
        self.db.executemany(
            "INSERT OR IGNORE INTO pages(pageid,title) VALUES (?,?)", pages)

    def add_categories(self, cats: list[str], depth: int):
        self.db.executemany("INSERT OR IGNORE INTO categories(title,depth) VALUES (?,?)",
                            [(category_title(c), depth) for c in cats])

    def category(self):
        return self.db.execute("SELECT title,depth,continuation,parents_done FROM categories "
                               "WHERE finished=0 ORDER BY depth,title LIMIT 1").fetchone()

    def page(self):
        return self.db.execute("SELECT pageid,title FROM pages WHERE checked=0 ORDER BY pageid LIMIT 1").fetchone()

    def record_page(self, pageid: int, matched: bool, title: str | None = None):
        with self.db:
            if title:
                self.db.execute("UPDATE pages SET title=?,checked=1,matched=? WHERE pageid=?",
                                (title, int(matched), pageid))
            else:
                self.db.execute("UPDATE pages SET checked=1,matched=? WHERE pageid=?",
                                (int(matched), pageid))

    def counts(self) -> dict[str, int]:
        counts = {}
        for key, sql in {
            "categories": "SELECT COUNT(*) FROM categories",
            "categories_done": "SELECT COUNT(*) FROM categories WHERE finished=1",
            "pages_discovered": "SELECT COUNT(*) FROM pages",
            "pages_checked": "SELECT COUNT(*) FROM pages WHERE checked=1",
            "matched": "SELECT COUNT(*) FROM pages WHERE matched=1",
        }.items():
            counts[key] = self.db.execute(sql).fetchone()[0]
        return counts

    def export(self, filename: Path) -> int:
        filename.parent.mkdir(parents=True, exist_ok=True)
        tmp = filename.with_suffix(filename.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8", newline="\n") as f:
            for (title,) in self.db.execute("SELECT DISTINCT title FROM pages WHERE matched=1 ORDER BY title"):
                f.write(canonical_url(title) + "\n")
        tmp.replace(filename)
        return self.counts()["matched"]


def category_title(text: str) -> str:
    return "Category:" + text.removeprefix("Category:").replace("_", " ").strip()


def fetch_parents(api: MediaWiki, title: str) -> list[str]:
    parents = []
    continuation = {}
    while True:
        result = api.query(action="query", prop="categories", titles=title,
                           cllimit="max", **continuation)
        for page in result.get("query", {}).get("pages", []):
            parents.extend(c["title"] for c in page.get("categories", []) if c["ns"] == 14)
        continuation = result.get("continue", {})
        if not continuation:
            return parents


def crawl_category(store: Store, api: MediaWiki, max_depth: int,
                   use_parents: bool = True):
    item = store.category()
    if not item:
        return False
    title, depth, continuation, parents_done = item
    if depth > max_depth:
        with store.db:
            store.db.execute("UPDATE categories SET finished=1 WHERE title=?", (title,))
        return True
    if use_parents and depth < max_depth and not parents_done:
        parents = [x for x in fetch_parents(api, title) if PARENT_RELEVANCE.search(x)]
        with store.db:
            store.add_categories(parents, depth + 1)
            store.db.execute("UPDATE categories SET parents_done=1 WHERE title=?", (title,))
    data = api.query(action="query", list="categorymembers", cmtitle=title,
                     cmtype="page|subcat", cmlimit="max",
                     **({"cmcontinue": continuation} if continuation else {}))
    members = data.get("query", {}).get("categorymembers", [])
    pages = [(p["pageid"], p["title"]) for p in members if p.get("ns") == 0]
    cats = [p["title"] for p in members if p.get("ns") == 14]
    token = data.get("continue", {}).get("cmcontinue")
    with store.db:
        store.add_pages(pages)
        if depth < max_depth:
            store.add_categories(cats, depth + 1)
        store.db.execute("UPDATE categories SET continuation=?, finished=? WHERE title=?",
                         (token, int(not token), title))
    return True


def check_one(store: Store, api: MediaWiki):
    page = store.page()
    if not page:
        return False
    pageid, title = page
    try:
        result = api.query(action="parse", pageid=pageid, prop="tocdata")
    except ValueError as error:
        # Deleted pages / unsupported page models should not block an entire crawl.
        logging.warning("Skipping pageid=%d: %s", pageid, error)
        store.record_page(pageid, False)
        return True
    parsed = result.get("parse", {})
    toc = parsed.get("tocdata", {})
    match = toc_has_proof(toc)
    store.record_page(pageid, match, parsed.get("title", title))
    return True


def sweep_allpages(store: Store, api: MediaWiki):
    continuation = store.db.execute("SELECT value FROM metadata WHERE key='apcontinue'").fetchone()
    opts = {"apcontinue": continuation[0]} if continuation else {}
    result = api.query(action="query", list="allpages", apnamespace=0, aplimit="max", **opts)
    pages = [(p["pageid"], p["title"]) for p in result.get("query", {}).get("allpages", [])]
    token = result.get("continue", {}).get("apcontinue")
    with store.db:
        store.add_pages(pages)
        if token:
            store.db.execute("INSERT INTO metadata(key,value) VALUES ('apcontinue',?) "
                             "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (token,))
        else:
            store.db.execute("DELETE FROM metadata WHERE key='apcontinue'")
            store.db.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES ('allpages_finished','1')")
    return bool(token)


def run_api(args, store: Store, api: MediaWiki):
    checks = 0
    steps = 0
    done_allpages = bool(store.db.execute("SELECT 1 FROM metadata WHERE key='allpages_finished'").fetchone())
    try:
        while True:
            did_discover = False
            if args.mode == "categories":
                did_discover = crawl_category(store, api, args.max_depth,
                                             use_parents=not args.no_parents)
            elif not done_allpages:
                did_discover = True
                done_allpages = not sweep_allpages(store, api)
            for _ in range(args.check_batch):
                if args.max_checks and checks >= args.max_checks:
                    break
                if not check_one(store, api):
                    break
                checks += 1
            steps += 1
            if steps % args.progress_every == 0:
                logging.info("requests=%d %s", api.requests, store.counts())
                store.export(args.output)
            if args.max_checks and checks >= args.max_checks:
                break
            if not did_discover and store.page() is None:
                break
    except RequestLimit:
        logging.info("Reached --max-requests budget; resume with same --state")
    finally:
        store.export(args.output)
        logging.info("Final: requests=%d %s", api.requests, store.counts())


def run_dump(args, store: Store):
    """Optional high-recall second pass. A restart rescans compressed input, deduping via SQLite."""
    filename = args.dump_file
    opener = bz2.open if filename.suffix == ".bz2" else gzip.open if filename.suffix == ".gz" else open
    processed = 0
    with opener(filename, "rb") as stream:
        events = ET.iterparse(stream, events=("start", "end"))
        _, root = next(events)
        for event, element in events:
            if event != "end" or element.tag.rsplit("}", 1)[-1] != "page":
                continue
            def child(name):
                return next((c for c in element if c.tag.rsplit("}", 1)[-1] == name), None)
            ns = child("ns")
            ident = child("id")
            title = child("title")
            if ns is not None and ns.text == "0" and ident is not None and title is not None:
                pageid = int(ident.text)
                exists = store.db.execute("SELECT checked FROM pages WHERE pageid=?", (pageid,)).fetchone()
                if not exists or exists[0] == 0:
                    revision = child("revision")
                    txt = ""
                    if revision is not None:
                        txt = next((n.text or "" for n in revision.iter()
                                    if n.tag.rsplit("}", 1)[-1] == "text"), "")
                    with store.db:
                        store.add_pages([(pageid, title.text or "")])
                        store.record_page(pageid, wikitext_has_proof(txt), title.text)
                    processed += 1
            root.clear()
            if processed and processed % 10000 == 0:
                store.export(args.output)
                logging.info("Dump scan: new pages=%d %s", processed, store.counts())
    store.export(args.output)
    logging.info("Dump completed: new pages=%d %s", processed, store.counts())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("categories", "allpages", "dump"), default="categories")
    parser.add_argument("--contact", help="Real email or public contact URL for Wikimedia User-Agent")
    parser.add_argument("--state", type=Path, default=Path(".harvest_runs/wikipedia_proof/state.sqlite3"))
    parser.add_argument("--output", type=Path, default=Path(".harvest_runs/wikipedia_proof/wikipedia_theorem_urls.txt"))
    parser.add_argument("--seed", action="append", default=[], help="Additional category (repeatable)")
    parser.add_argument("--max-depth", type=int, default=9)
    parser.add_argument("--no-parents", action="store_true")
    parser.add_argument("--max-checks", type=int, default=0, help="Max pages inspected THIS run (0=unlimited)")
    parser.add_argument("--max-requests", type=int, default=0, help="Max API attempts THIS run (0=unlimited)")
    parser.add_argument("--check-batch", type=int, default=20)
    parser.add_argument("--progress-every", type=int, default=5)
    parser.add_argument("--delay", type=float, default=1.5, help="Minimum seconds between requests")
    parser.add_argument("--dump-file", type=Path, help="pages-articles XML(.bz2/.gz) for --mode dump")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    if args.max_depth < 1 or args.check_batch < 1 or args.progress_every < 1 or args.delay < 0:
        parser.error("Invalid depth, check batch, progress frequency, or delay")
    if args.mode == "dump" and not args.dump_file:
        parser.error("--mode dump requires --dump-file")
    if args.mode != "dump" and not args.contact:
        parser.error("Supply --contact with an actual project contact address/URL")
    store = Store(args.state)
    try:
        if args.mode == "categories":
            store.seed(list(SEEDS) + args.seed)
        if args.mode == "dump":
            run_dump(args, store)
        else:
            run_api(args, store, MediaWiki(args.contact, delay=args.delay,
                                          max_requests=args.max_requests))
    finally:
        store.db.close()


if __name__ == "__main__":
    main()

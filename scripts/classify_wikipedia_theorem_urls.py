#!/usr/bin/env python3
"""Conservatively classify English Wikipedia proof-heading URLs.

Uses only article title, Wikipedia category labels, and short introductory
description. Does not inspect theorem statements, proofs or truth.
Every original URL receives a result; uncertain pages are NEVER dropped.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://en.wikipedia.org/w/api.php"
AGENT = "mathThmWikipediaURLTriage/1.0 (https://github.com/Zengez/mathThm)"
RESULT_CATEGORY = re.compile(
    r"\btheorems\b|\blemmas\b|\bmathematical (?:inequalities|identities|results|principles)\b|"
    r"\binequalities in mathematics\b|\bidentities in mathematics\b", re.I
)
NOT_RESULT_CATEGORY = re.compile(
    r"\bproofs?\b|\bproving\b|\bprovers?\b|\bassistants?\b|"
    r"\bsoftware\b|\bprograms?\b|\blists?\b|\bconjectures\b|"
    r"\bbiographies\b|\bhistory\b", re.I
)
NON_THEOREM_PAGE_TITLE = re.compile(
    r"^(?:proof of|proofs of|list of|lists of|"
    r"proof assistant|automated reasoning)\b|"
    r"\btheorem prov(?:ing|er|ers)\b", re.I
)
NON_THEOREM_SUBJECT = re.compile(
    r"\b(?:is|was) (?:a|an|the) (?:[a-z-]+\s+){0,5}"
    r"(?:board game|video game|logician|mathematician|philosopher|"
    r"software system|computer program|programming language|"
    r"theorem prover|proof assistant|diagram|illustration|"
    r"television show|politician|actor|musician|novel|film)\b", re.I
)
MATH_CATEGORY = re.compile(
    r"mathemat|algebra|analysis|analytic|topolog|geometr|number theory|"
    r"combinator|calculus|set theory|probabil|graph theory|ring theory|"
    r"group theory|linear algebra|arithmetic|complex variable|"
    r"functional analysis|real analysis|mathematical logic|"
    r"order theory|differential equation|number-theoretic|"
    r"theoretical computer science|formal logic|category theory|"
    r"operator theory|metric space|measure theory|"
    r"discrete math|dynamical system", re.I
)
RESULT_TITLE = re.compile(r"\btheorems?\b|\blemmas?\b", re.I)
OTHER_RESULT_TITLE = re.compile(
    r"\binequalit(?:y|ies)\b|\bidentit(?:y|ies)\b|\bcriteria?\b|"
    r"\bprinciples?\b|\bformulas?\b|\bbounds?\b|\blaws?\b|\btests?\b", re.I
)
INTRO_MATH = re.compile(
    r"mathematical|mathematics|in (?:topology|algebra|geometry|number theory|"
    r"analysis|combinatorics|set theory|calculus|probability theory)|"
    r"\b(?:mathematical )?theorem\b|\blemma\b|\bproof in mathematics\b", re.I
)
INTRO_RESULT = re.compile(
    r"\b(?:is|was) (?:a|an) (?:fundamental |important |classical |well-known )?"
    r"(?:mathematical )?(?:theorem|lemma|inequality|identity|result)\b|"
    r"\b(?:theorem|lemma) (?:states|asserts|establishes|shows)\b", re.I
)
NONMATH_CATEGORY = re.compile(
    r"elections?|sports?|football|basketball|cricket|baseball|tennis|"
    r"politic|politicians?|films?|movies?|television|novels?|"
    r"albums?|songs?|discograph|musicians?|video games?|"
    r"buddhis|christian|islam|religio|"
    r"literatur|literary|novelists?|legal cases|court cases|"
    r"military history|military personnel|historical events|"
    r"political history|actors|actresses|"
    r"television series|characters in fiction|"
    r"disease outbreaks|medical diseases|medical conditions", re.I
)
NONMATH_INTRO = re.compile(
    r"\b(?:is|was) (?:an? |the )"
    r"(?:american |british |japanese |indian |french |canadian |"
    r"irish |german |english |fictional |animated |)"
    r"(?:song|album|film|movie|television series|novel|"
    r"election|politician|musician|actor|actress|"
    r"religious text|video game|book|disease outbreak|"
    r"court case|legal doctrine)\b", re.I
)


def title_from_url(url: str) -> str:
    p = urllib.parse.urlsplit(url.strip())
    if p.scheme != "https" or p.netloc != "en.wikipedia.org" or not p.path.startswith("/wiki/"):
        raise ValueError("Not an English Wikipedia article URL: " + url)
    title = urllib.parse.unquote(p.path[len("/wiki/"):]).replace("_", " ")
    if not title or title.startswith(("Category:", "Talk:", "User:", "File:")):
        raise ValueError("Not a main-namespace article: " + url)
    return title


def normalize_title(title: str) -> str:
    return title.replace("_", " ").strip().casefold()


def classify(title: str, categories: list[str], intro: str, missing: bool = False):
    """Return (decision, reason). Absent evidence => needs_review."""
    if missing:
        return "needs_review", "Wikipedia page missing/redirect uncertain; preserve URL"
    categories_text = " | ".join(categories)
    theorem_category = any(
        RESULT_CATEGORY.search(category) and not NOT_RESULT_CATEGORY.search(category)
        for category in categories
    )
    theorem_title = bool(RESULT_TITLE.search(title))
    if NON_THEOREM_PAGE_TITLE.search(title):
        return "needs_review", "Article is a proof, list, or theorem-proving tool rather than a dedicated theorem page"
    if not theorem_title and NON_THEOREM_SUBJECT.search(intro):
        return "needs_review", "Intro identifies a person, game, software, or other non-theorem subject"
    math_category = bool(MATH_CATEGORY.search(categories_text))
    other_result_title = bool(OTHER_RESULT_TITLE.search(title))
    math_intro = bool(INTRO_MATH.search(intro))
    result_intro = bool(INTRO_RESULT.search(intro))
    nonmath_category = bool(NONMATH_CATEGORY.search(categories_text))
    nonmath_intro = bool(NONMATH_INTRO.search(intro))
    if theorem_category:
        return "accepted", "Explicit Wikipedia mathematical-result/theorem/lemma category"
    if theorem_title and (math_category or math_intro):
        return "accepted", "Theorem/lemma title plus mathematical-category or introduction evidence"
    if other_result_title and math_category and result_intro:
        return "accepted", "Named mathematical result supported by mathematical category and introduction"
    if (nonmath_category or nonmath_intro) and not (
        theorem_title or other_result_title or math_category or math_intro or result_intro
    ):
        return "rejected", "Explicitly nonmathematical category/introduction; no mathematical-result signal"
    return "needs_review", "Insufficient evidence to establish or exclude a mathematical theorem"


def atomic_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)


class Wikipedia:
    def __init__(self, delay: float):
        self.delay = delay
        self.last = 0.0
        self.calls = 0

    def query(self, **kwargs):
        params = {"action": "query", "format": "json", "formatversion": 2,
                  "maxlag": 5, "redirects": 1, **kwargs}
        url = API + "?" + urllib.parse.urlencode(params)
        for attempt in range(7):
            wait = self.delay - (time.monotonic() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.monotonic()
            self.calls += 1
            req = urllib.request.Request(url, headers={"User-Agent": AGENT,
                                                       "Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=55) as response:
                    data = json.load(response)
                if "error" in data:
                    if data["error"].get("code") == "maxlag":
                        raise RuntimeError("MediaWiki maxlag: " + str(data["error"]))
                    raise ValueError("MediaWiki query rejected: " + str(data["error"]))
                return data
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                    OSError, ValueError, RuntimeError) as exc:
                if isinstance(exc, urllib.error.HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                    raise
                if isinstance(exc, ValueError):
                    raise
                if attempt == 6:
                    raise
                delay = min(120, 2 ** attempt + 3)
                if isinstance(exc, urllib.error.HTTPError):
                    try:
                        delay = max(delay, min(120, float(exc.headers.get("Retry-After", "0"))))
                    except ValueError:
                        pass
                logging.warning("Wikipedia request failed (%s), retrying in %.1fs", exc, delay)
                time.sleep(delay)
        raise AssertionError("Unreachable")


def fetch_metadata(client: Wikipedia, batch: list[tuple[str, str]]) -> list[dict]:
    """Fetch category labels and short intro for each URL, with full API continuation."""
    titles = [title for _, title in batch]
    by_title = {}
    aliases = {}
    continuation = {}
    for _ in range(1000):
        data = client.query(
            titles="|".join(titles), prop="categories|extracts",
            cllimit="max", clshow="!hidden", exintro=1, explaintext=1,
            exsentences=2, **continuation)
        query = data.get("query", {})
        for entry in query.get("normalized", []) + query.get("redirects", []):
            aliases[normalize_title(entry["from"])] = normalize_title(entry["to"])
        for page in query.get("pages", []):
            key = normalize_title(page.get("title", ""))
            if not key:
                continue
            record = by_title.setdefault(key, {"title": page["title"], "categories": [],
                                               "intro": "", "missing": False})
            record["missing"] = bool(page.get("missing", False))
            if page.get("extract") and not record["intro"]:
                record["intro"] = page["extract"][:900]
            record["categories"].extend(c["title"].removeprefix("Category:")
                                        for c in page.get("categories", []))
        continuation = data.get("continue", {})
        if not continuation:
            break
    else:
        raise RuntimeError("Pagination exceeded 1000 calls; refusing incomplete metadata")
    result = []
    for url, title in batch:
        key = normalize_title(title)
        seen = set()
        while key in aliases and key not in seen:
            seen.add(key)
            key = aliases[key]
        rec = by_title.get(key, {"title": title, "categories": [], "intro": "",
                                 "missing": True})
        result.append({"url": url, "title": title, "resolved_title": rec["title"],
                       "categories": sorted(set(rec["categories"])),
                       "intro": rec["intro"], "missing": rec["missing"]})
    return result


def read_urls(path: Path) -> list[str]:
    urls = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(urls) != len(set(urls)):
        raise ValueError("Input URL list must be deduplicated")
    for url in urls:
        title_from_url(url)
    return urls


def export_results(outdir: Path, rows: list[dict], total: int):
    if len(rows) != len({r["url"] for r in rows}):
        raise ValueError("Duplicate cached URL metadata")
    ordered = sorted(rows, key=lambda r: r["url"])
    decisions = []
    for entry in ordered:
        decision, reason = classify(entry["resolved_title"], entry["categories"],
                                    entry["intro"], missing=entry["missing"])
        decisions.append({**entry, "decision": decision, "reason": reason})
    for label in ("accepted", "rejected", "needs_review"):
        sub = [r for r in decisions if r["decision"] == label]
        atomic_write(outdir / (label + "_urls.txt"),
                     "".join(r["url"] + "\n" for r in sub))
    review = [r for r in decisions if r["decision"] == "needs_review"]
    atomic_write(outdir / "review_queue.jsonl",
                 "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in review))
    for index in range(4):
        lane = [r for r in review if int(hashlib.sha256(r["url"].encode()).hexdigest()[:8], 16) % 4 == index]
        atomic_write(outdir / f"review_worker_{index + 1}.jsonl",
                     "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in lane))
    atomic_write(outdir / "decisions.jsonl",
                 "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in decisions))
    counts = {label: sum(r["decision"] == label for r in decisions)
              for label in ("accepted", "rejected", "needs_review")}
    counts["processed"] = len(decisions)
    counts["total"] = total
    counts["remaining_metadata"] = total - len(decisions)
    atomic_write(outdir / "progress.json", json.dumps(counts, indent=2) + "\n")
    report = ("## Wikipedia proof-heading URL classification\n\n"
              f"- Analyzed: **{len(decisions)} / {total}** URLs\n"
              f"- Auto-accepted: **{counts['accepted']}**\n"
              f"- Auto-rejected: **{counts['rejected']}**\n"
              f"- Needs review: **{counts['needs_review']}**\n"
              f"- Not yet analyzed: **{counts['remaining_metadata']}**\n"
              "- Scope: theorem identity only; no mathematical or proof validation.\n"
              "- Original harvest remains unchanged.\n")
    atomic_write(outdir / "REPORT.md", report)
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(report)
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--max-batches", type=int, default=0,
                        help="Bound run for smoke testing; zero = all remaining")
    args = parser.parse_args(argv)
    if not 1 <= args.batch_size <= 20 or args.delay < 0 or args.max_batches < 0:
        parser.error("Invalid batch size/delay/max-batches")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    urls = read_urls(args.input)
    fingerprint = hashlib.sha256(("\n".join(urls) + "\n").encode()).hexdigest()
    outdir = args.output_dir
    outdir.mkdir(parents=True, exist_ok=True)
    manifest_file = outdir / "source_manifest.json"
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        if manifest != {"sha256": fingerprint, "total": len(urls), "batch_size": args.batch_size}:
            raise ValueError("Input changed; use new output directory, do not merge checkpoints")
    else:
        atomic_write(manifest_file, json.dumps(
            {"sha256": fingerprint, "total": len(urls), "batch_size": args.batch_size}, indent=2) + "\n")
    cli = Wikipedia(args.delay)
    processed = 0
    try:
        for i in range(0, len(urls), args.batch_size):
            index = i // args.batch_size
            cache = outdir / "batches" / f"{index:04d}.jsonl"
            if cache.exists():
                continue
            if args.max_batches and processed >= args.max_batches:
                break
            batch = [(url, title_from_url(url)) for url in urls[i:i + args.batch_size]]
            rows = fetch_metadata(cli, batch)
            if [r["url"] for r in rows] != [url for url, _ in batch]:
                raise RuntimeError("Metadata URL alignment failure")
            atomic_write(cache, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
            processed += 1
            if processed % 10 == 0:
                logging.info("New batches %d; API requests %d", processed, cli.calls)
    finally:
        rows = []
        for cache in sorted((outdir / "batches").glob("*.jsonl")) if (outdir / "batches").exists() else []:
            rows.extend(json.loads(line) for line in cache.read_text(encoding="utf-8").splitlines() if line)
        known = set(urls)
        if any(r["url"] not in known for r in rows):
            raise RuntimeError("Unexpected URL in cached metadata")
        counts = export_results(outdir, rows, len(urls))
        logging.info("Requests=%d | %s", cli.calls, counts)


if __name__ == "__main__":
    main()

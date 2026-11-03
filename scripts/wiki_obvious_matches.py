#!/usr/bin/env python3
"""Conservative Wikipedia -> already-published mathThm theorem proof-link pass.

Match only a UNIQUE normalized theorem title. No proof validation, theorem
generation, rewriting, fuzzy equivalence, or ambiguous duplicate suppression.
Only attach an external link if Wikipedia actually exposes a proof heading.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit, urlencode
from urllib.request import Request, urlopen

HEADINGS = re.compile(
    r"(?i)^(?:proof|proofs|proof sketch|sketch of proof|proof outline|outline of proof|"
    r"proof of theorem|demonstration)(?:\s+[0-9]+)?$")
AGENT = "mathThm-wikipedia-obvious-match/1.0 (https://github.com/Zengez/mathThm)"
DATE = "2026-11-03"


def title_from_url(url: str) -> str:
    path = urlsplit(url).path
    if "/wiki/" not in path:
        raise ValueError("not a Wikipedia article URL: " + url)
    return unquote(path.split("/wiki/", 1)[1]).replace("_", " ")


def normalized(text: str, theorem_title: bool = False) -> str:
    if theorem_title:
        text = re.sub(r"^(?:theorem|lemma|proposition|corollary|other result)\s*[—–:-]\s*",
                      "", text, flags=re.I)
    else:
        # A proof-of-X page can provide a proof of theorem X.
        text = re.sub(r"^proofs? of\s+", "", text, flags=re.I)
    text = text.casefold().replace("group theory", "groups")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def get(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": AGENT, "Accept": "application/json,text/html"})
    with urlopen(req, timeout=15) as resp:
        return resp.read(5_000_000)


class HeadingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.tag = ""
        self.anchor = ""
        self.text = []
        self.headings = []

    def handle_starttag(self, tag, attrs):
        if tag in ("h2", "h3", "h4"):
            self.active = True
            self.tag = tag
            self.anchor = dict(attrs).get("id", "")
            self.text = []
        elif self.active and tag == "span" and not self.anchor:
            self.anchor = dict(attrs).get("id", "")

    def handle_data(self, text):
        if self.active:
            self.text.append(text)

    def handle_endtag(self, tag):
        if self.active and tag == self.tag:
            self.headings.append((unescape("".join(self.text)).strip(), self.anchor))
            self.active = False


def is_proof_heading(heading: str, page_title: str) -> bool:
    if HEADINGS.fullmatch(heading):
        return True
    # E.g. the Wikipedia heading "Proofs of the extreme value theorem".
    h = normalized(heading)
    title = normalized(page_title)
    return (h.startswith(("proof of ", "proofs of ")) and
            len(title) >= 10 and title in h)


def find_section(url: str, wait: float = 0) -> tuple[str | None, str]:
    title = title_from_url(url)
    # This page's proof subsection is explicitly visible in the article,
    # but the MediaWiki section parser can miss its descriptive heading.
    # Verified on the article on 2026-11-03; not a theorem/proof audit.
    known_proof_sections = {
        "Extreme value theorem": "Proofs_of_the_extreme_value_theorem",
    }
    if title in known_proof_sections:
        return url.split("#")[0] + "#" + known_proof_sections[title], "visible_article_heading"
    api = "https://en.wikipedia.org/w/api.php?" + urlencode({
        "action": "parse", "page": title, "prop": "sections", "format": "json",
    })
    try:
        result = json.loads(get(api))
        for section in result.get("parse", {}).get("sections", []):
            heading = re.sub(r"<[^>]+>", "", section.get("line", "")).strip()
            anchor = section.get("anchor")
            if is_proof_heading(heading, title) and anchor:
                return url.split("#")[0] + "#" + quote(anchor, safe=":-._"), "api"
    except (OSError, HTTPError, URLError, ValueError, TimeoutError):
        pass

    # HTML fallback: use the real heading id, never fabricate "#Proof".
    try:
        parser = HeadingParser()
        parser.feed(get(url).decode("utf-8", errors="replace"))
        for heading, anchor in parser.headings:
            if is_proof_heading(heading, title) and anchor:
                return url.split("#")[0] + "#" + quote(anchor, safe=":-._"), "html"
    except (OSError, HTTPError, URLError, ValueError, TimeoutError):
        return None, "unavailable"
    finally:
        if wait:
            time.sleep(wait)
    return None, "no_proof_section"


def run(catalog: Path, accepted: Path, output: Path, delay: float) -> dict:
    theorems = json.loads(catalog.read_text(encoding="utf-8"))["records"]
    urls = [x.strip() for x in accepted.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(urls) != len(set(urls)):
        raise ValueError("duplicate accepted Wikipedia URLs")
    by_title = defaultdict(list)
    for theorem in theorems:
        key = normalized(theorem.get("title") or "", theorem_title=True)
        if key and len(key) >= 7 and not key.isdigit():
            by_title[key].append(theorem)

    report = []
    proof_links = defaultdict(list)
    for i, url in enumerate(urls):
        title = title_from_url(url)
        key = normalized(title)
        matches = by_title.get(key, [])
        row = {"url": url, "wikipedia_title": title,
               "method": "unique_normalized_title_only",
               "decision": "unmatched"}
        if len(matches) > 1:
            row["reason"] = "more_than_one_published_theorem_has_this_title"
        elif not matches:
            row["reason"] = "no_unique_exact_title_match"
        else:
            theorem = matches[0]
            proof, method = find_section(url, delay)
            if not proof:
                row["reason"] = "no_confirmed_wikipedia_proof_section"
                row["section_lookup"] = method
                row["possible_theorem_id"] = theorem["id"]
            else:
                row.update({
                    "decision": "matched",
                    "reason": "unique_title_match_and_confirmed_proof_section",
                    "theorem_id": theorem["id"],
                    "proof_url": proof,
                    "section_lookup": method,
                })
                proof_links[theorem["id"]].append({
                    "url": proof,
                    "label": "Link to proof (Wikipedia)",
                    "source_article": url,
                    "match_basis": "unique_normalized_title",
                    "proof_review": "link_only_not_mathematically_audited",
                    "found_on": DATE,
                })
        report.append(row)
        if i % 100 == 99:
            print(f"Processed {i+1}/{len(urls)} Wikipedia URLs", flush=True)

    # The overlay is consumed by the publication script and survives rebuilding.
    output.mkdir(parents=True, exist_ok=True)
    (output / "matches.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n"
                for row in report if row["decision"] == "matched"), encoding="utf-8")
    (output / "decisions.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in report), encoding="utf-8")
    unmatched = [row["url"] for row in report if row["decision"] == "unmatched"]
    (output / "unmatched_urls.txt").write_text("\n".join(unmatched) + "\n", encoding="utf-8")
    mapping = {"schema": "maththm.wikipedia-proof-links.v1",
               "source": "Wikipedia final reviewed accepted URLs (2026-11-03)",
               "links_by_theorem_id": dict(sorted(proof_links.items()))}
    (output / "wikipedia_proof_links.json").write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    counts = Counter(r["decision"] for r in report)
    summary = {"total_accepted_urls": len(urls), "published_theorems_compared": len(theorems),
               "matched_urls": counts["matched"], "unmatched_urls": counts["unmatched"],
               "theorems_receiving_links": len(proof_links),
               "reason_counts": dict(Counter(row["reason"] for row in report)),
               "method": "unique normalized title and verified Wikipedia proof heading",
               "note": "Ambiguous or unconfirmed matches are intentionally retained."}
    (output / "REPORT.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", type=Path, required=True)
    p.add_argument("--accepted", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--delay", type=float, default=0.2)
    opts = p.parse_args()
    run(opts.catalog, opts.accepted, opts.output, opts.delay)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Stage A: prepare Wikipedia result-page statement excerpts and *tentative* splits.

No LLM, mathematical correctness check, theorem admission, or proof audit.
Four independent lanes fetch the lead/first statement sections; an integrator
writes recoverable candidate records and editorial queues with exact URL IDs.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit, urlencode, quote
from urllib.request import Request, urlopen

TOTAL_LANES = 4
USER_AGENT = "mathThm-Wikipedia-StageA/1.0 (https://github.com/Zengez/mathThm)"
STOP_SECTIONS = re.compile(
    r"(?i)^(?:proof(?:s|\s+.*)?|history|background|references|notes|"
    r"external links|further reading|see also|applications|examples|"
    r"generalizations|related results|discussion|derivation|"
    r"historical background|bibliography|sources)$")
LEAD_PRIORITY = re.compile(
    r"(?i)\b(theorem|lemma|proposition|identity|inequality|"
    r"states that|asserts that|holds that|if and only if|"
    r"implies that|there exists|for every|for any|for all|"
    r"can be expressed|is equivalent|given any|is equal to)\b")
EXACT_IF_THEN = re.compile(
    r"(?is)^(?:(?:the )?theorem (?:states|asserts|says) that\s+)?"
    r"if\s+(?P<h>.{12,430}?),\s*then\s+(?P<c>.{12,800}?)\.?\s*$")
EXACT_LET_THEN = re.compile(
    r"(?is)^(?:let|suppose|assume)\s+(?P<h>.{12,380}?)\.\s*"
    r"then\s+(?P<c>.{12,700}?)\.?\s*$")
VOID = {"br", "hr", "img", "input", "meta", "link", "source", "wbr", "area"}
SKIP = {"script", "style", "table", "figure", "nav"}


def title_from_url(url: str) -> str:
    path = urlsplit(url).path
    if urlsplit(url).netloc != "en.wikipedia.org" or not path.startswith("/wiki/"):
        raise ValueError("Invalid English Wikipedia URL: " + url)
    return unquote(path[len("/wiki/"):]).replace("_", " ")


def stable_id(url: str) -> str:
    return "candidate.wikipedia." + hashlib.sha256(url.encode()).hexdigest()[:20]


def clean_text(value: str) -> str:
    return " ".join(unescape(value).replace("\u00a0", " ").split())


def latex_alt(value: str) -> str:
    """Retain the source's MathJax/TeX alternate text without inventing math."""
    text = unescape(value).strip()
    if text.startswith(r"{\displaystyle ") and text.endswith("}"):
        text = text[len(r"{\displaystyle "):-1]
    if text.startswith(r"{\textstyle ") and text.endswith("}"):
        text = text[len(r"{\textstyle "):-1]
    return "$" + text + "$" if text else ""


class TopText(HTMLParser):
    """Read visible top article paragraphs (with math alttext) until proof/history."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.section = "Lead"
        self.parts = []
        self.paragraph_depth = 0
        self.heading = None
        self.heading_parts = []
        self.skip_depth = 0
        self.math_depth = 0
        self.stopped = False

    def handle_starttag(self, tag, attrs):
        if self.stopped:
            return
        att = dict(attrs)
        if self.skip_depth:
            if tag not in VOID:
                self.skip_depth += 1
            return
        klass = att.get("class", "")
        if tag in SKIP or ("reference" in klass and tag == "sup") or (
                tag == "div" and any(x in klass for x in
                    ("hatnote", "navbox", "thumb", "toc", "mw-references-wrap", "metadata"))):
            self.skip_depth = 1
            return
        if tag in ("h2", "h3") and not self.paragraph_depth:
            self.heading = tag
            self.heading_parts = []
            return
        if tag == "p":
            self.paragraph_depth += 1
            if self.paragraph_depth == 1:
                self.parts = []
            return
        if tag == "math" and self.paragraph_depth:
            self.math_depth += 1
            if self.math_depth == 1:
                self.parts.append(" " + latex_alt(att.get("alttext", "")) + " ")
            return
        if (tag == "img" and self.paragraph_depth and not self.math_depth
                and "mwe-math-fallback-image" in klass):
            self.parts.append(" " + latex_alt(att.get("alt", "")) + " ")

    def handle_endtag(self, tag):
        if self.stopped:
            return
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "math" and self.math_depth:
            self.math_depth -= 1
            return
        if self.heading == tag:
            heading = clean_text("".join(self.heading_parts))
            if STOP_SECTIONS.match(heading):
                self.stopped = True
            elif heading:
                self.section = heading[:130]
            self.heading = None
            return
        if tag == "p" and self.paragraph_depth:
            self.paragraph_depth -= 1
            if not self.paragraph_depth:
                paragraph = clean_text("".join(self.parts))
                if len(paragraph) >= 24 and len(self.blocks) < 16:
                    self.blocks.append({"section": self.section,
                                        "text": paragraph[:2500]})

    def handle_data(self, data):
        if self.stopped or self.skip_depth or self.math_depth:
            return
        if self.heading:
            self.heading_parts.append(data)
        elif self.paragraph_depth:
            self.parts.append(data)


def get_bytes(url: str) -> bytes:
    for retry in range(3):
        try:
            req = Request(url, headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json,text/html;q=0.9",
            })
            with urlopen(req, timeout=22) as response:
                raw = response.read(8_000_000)
            if len(raw) >= 8_000_000:
                raise ValueError("response too large")
            return raw
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            if retry == 2 or (
                    isinstance(exc, HTTPError) and exc.code not in (429, 500, 502, 503, 504)):
                raise
            time.sleep(1.5 * (retry + 1))
    raise RuntimeError("exhausted network retries")


def get_html(url: str) -> tuple[str, str]:
    title = title_from_url(url)
    query = urlencode({
        "action": "parse", "page": title, "prop": "text",
        "format": "json", "formatversion": "2", "disabletoc": "1",
    })
    errors = []
    try:
        obj = json.loads(get_bytes("https://en.wikipedia.org/w/api.php?" + query))
        parsed = obj.get("parse") or {}
        text = parsed.get("text")
        if isinstance(text, str) and text:
            return text[:600_000], "mediawiki_parse_html"
        errors.append(str(obj.get("error") or "empty API response"))
    except (HTTPError, URLError, OSError, ValueError, TimeoutError) as exc:
        errors.append(type(exc).__name__ + ": " + str(exc)[:150])
    try:
        title_path = quote(title.replace(" ", "_"), safe="():,'-._~")
        html = get_bytes("https://en.wikipedia.org/wiki/" + title_path)
        return html.decode("utf-8", errors="replace")[:600_000], "article_html_fallback"
    except (HTTPError, URLError, OSError, ValueError, TimeoutError) as exc:
        errors.append(type(exc).__name__ + ": " + str(exc)[:150])
    raise RuntimeError("; ".join(errors))


def snippet(blocks: list[dict]) -> tuple[str, str, str]:
    """Return top excerpt and strongest source paragraph, not an authored theorem."""
    if not blocks:
        return "", "", ""
    selected = []
    size = 0
    for block in blocks:
        if size >= 4600 or len(selected) >= 10:
            break
        item = block["text"][:1600]
        selected.append({"section": block["section"], "text": item})
        size += len(item)
    excerpt = "\n\n".join(
        ("[" + p["section"] + "] " if p["section"] != "Lead" else "") + p["text"]
        for p in selected)
    scores = []
    for i, block in enumerate(selected):
        p = block["text"]
        score = int(bool(LEAD_PRIORITY.search(p))) * 5
        score += int(bool(re.search(r"(?i)^(if|let|suppose|assume|for every|for any|given)\b", p))) * 4
        score += int(bool(re.search(r"(?i)\b(stated? as follows|formulated as|can be written)\b", p))) * 2
        score += int("$" in p) * 2
        score += int(bool(re.search(r"(?i)statement|formulation|theorem", block["section"]))) * 2
        score -= int(bool(re.search(r"(?i)^in (?:mathematics|physics),? \w+ is a (?:type|class|branch)", p))) * 3
        score -= i  # Earlier introduction preferred to later consequences.
        scores.append(score)
    best = selected[max(range(len(selected)), key=scores.__getitem__)]
    return excerpt, best["text"], best["section"]


def mechanical_split(statement: str) -> tuple[list[str], list[str], str]:
    """Only syntax-first splits; never claim these are validated mathematically."""
    if not statement or len(statement) > 1100:
        return [], [], "needs_interpretation"
    for pattern in (EXACT_IF_THEN, EXACT_LET_THEN):
        match = pattern.match(statement)
        if match:
            hyp = clean_text(match.group("h")).rstrip(".; ")
            con = clean_text(match.group("c")).rstrip(".; ")
            if (len(hyp) >= 12 and len(con) >= 12 and
                    not re.search(r"\b(?:however|although|whereas)\b", hyp, flags=re.I)):
                return [hyp], [con], "mechanical_suggestion"
    return [], [], "needs_interpretation"


def prepare_one(url: str, position: int, delay: float) -> dict:
    title = title_from_url(url)
    item = {
        "candidate_id": stable_id(url), "input_index": position,
        "url": url, "title": title, "worker": position % TOTAL_LANES + 1,
        "source_stage": "wikipedia_top_before_proof",
        "source_statement_excerpt": None, "source_excerpt": None,
        "source_section": None, "hypotheses": [], "conclusions": [],
        "split_status": "fetch_failed",
        "source_fidelity": "html_text_extraction_not_source_transcription_reviewed",
        "mathematical_review": "not_reviewed",
    }
    try:
        html, extraction = get_html(url)
        parser = TopText()
        parser.feed(html)
        excerpt, proposed, section = snippet(parser.blocks)
        item.update(source_excerpt=excerpt or None,
                    source_statement_excerpt=proposed or None,
                    source_section=section or None,
                    extraction_method=extraction,
                    excerpt_paragraph_count=len(parser.blocks))
        if proposed:
            h, c, state = mechanical_split(proposed)
            item.update(hypotheses=h, conclusions=c, split_status=state)
        else:
            item["split_status"] = "no_statement_in_top"
    except (ValueError, RuntimeError, HTTPError, URLError, OSError, TimeoutError) as exc:
        item["fetch_error"] = (type(exc).__name__ + ": " + str(exc))[:350]
    if delay:
        time.sleep(delay)
    return item


def read_urls(path: Path) -> list[str]:
    urls = [s.strip() for s in path.read_text(encoding="utf-8").splitlines() if s.strip()]
    if not urls or len(urls) != len(set(urls)):
        raise ValueError("Empty URL file or duplicate input URLs")
    for url in urls:
        title_from_url(url)
    return urls


def dump_jsonl(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                    encoding="utf-8")


def lane_run(url_file: Path, lane: int, output: Path, delay: float, limit: int):
    urls = read_urls(url_file)
    assigned = [(i, url) for i, url in enumerate(urls)
                if i % TOTAL_LANES == lane - 1]
    if limit:
        assigned = assigned[:limit]
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for j, (i, url) in enumerate(assigned, 1):
        rows.append(prepare_one(url, i, delay))
        if j % 30 == 0:
            dump_jsonl(output / f"worker-{lane}.jsonl", rows)
            print(f"Lane {lane}: {j}/{len(assigned)} complete", flush=True)
    dump_jsonl(output / f"worker-{lane}.jsonl", rows)
    print(f"Lane {lane} complete: {dict(Counter(x['split_status'] for x in rows))}", flush=True)


def merge(url_file: Path, input_dir: Path, output: Path):
    urls = read_urls(url_file)
    if len(urls) != 1121:
        raise ValueError(f"Expected frozen 1121 unmatched URLs; got {len(urls)}")
    rows = []
    for lane in range(1, TOTAL_LANES + 1):
        path = input_dir / f"worker-{lane}.jsonl"
        if not path.exists():
            raise ValueError(f"Missing lane {lane}")
        rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line)
    rows.sort(key=lambda x: x["input_index"])
    if (len(rows) != len(urls) or
            any(row["url"] != urls[i] or row["input_index"] != i
                or row["worker"] != i % TOTAL_LANES + 1 for i, row in enumerate(rows)) or
            len({row["candidate_id"] for row in rows}) != len(urls)):
        raise ValueError("Incomplete/colliding four-lane outputs")
    output.mkdir(parents=True, exist_ok=True)
    counts = Counter(row["split_status"] for row in rows)
    for lane in range(1, TOTAL_LANES + 1):
        assigned = [r for r in rows if r["worker"] == lane]
        held = [r for r in assigned if r["split_status"] != "mechanical_suggestion"]
        suggested = [r for r in assigned if r["split_status"] == "mechanical_suggestion"]
        dest = output / f"worker-{lane}"
        dump_jsonl(dest / "needs_interpretation.jsonl", held)
        dump_jsonl(dest / "mechanical_suggestions.jsonl", suggested)
        (dest / "PROMPT.md").write_text(
            f"""# Wikipedia Stage A — worker {lane} (exclusive lane)

Repository: Zengez/mathThm
Base branch: work/wikipedia-stage-a-20261103
Input: work/wikipedia-stage-a/20261103/worker-{lane}/needs_interpretation.jsonl

Review your entire *assigned* queue (currently {len(held)} rows). Only split the
Wikipedia top excerpt into an accurate theorem statement, separate hypotheses
and conclusions, and preserve quantified conditions and scope.
Use `source_excerpt`, `source_statement_excerpt`, `source_section`, and the
live Wikipedia article when genuinely necessary. An article may contain multiple
statements; extract one distinct central result first and flag others explicitly.
**Do not** invent conditions, assume a theorem from the page title, collapse
two-direction equivalences, check proof correctness, or perform another
duplicate search. A difficult/unclear case may be held, not guessed.

Write your own results to `work/wikipedia-stage-a/20261103/worker-{lane}/
editorial_decisions.jsonl` on your own branch
`work/wikipedia-stage-a/worker-{lane}`, without editing other workers'
files. Each decision must retain `candidate_id`, `url`, `source_statement_excerpt`,
`statement` (or null), `hypotheses`, `conclusions`, and status
(`standalone_prepared` or `held_for_source_clarity`) with a concise reason.
Work in batches; save results incrementally, resuming by candidate ID only.

The {len(suggested)} mechanically split cases for this lane are separate in
`mechanical_suggestions.jsonl`. These are **draft suggestions, not verified
mathematical formulations**. Do not promote them automatically to the public
catalog. This work is statement preparation only, not a proof review.
""", encoding="utf-8")
    report = {
        "schema": "maththm.wikipedia-stage-a-prep.v1",
        "source": "work/wikipedia-obvious-match-pass/unmatched_urls.txt",
        "total_source_urls": len(urls),
        "processed": len(rows),
        "split_counts": dict(sorted(counts.items())),
        "manual_items": sum(counts[s] for s in counts if s != "mechanical_suggestion"),
        "suggested_items": counts["mechanical_suggestion"],
        "worker_counts": {
            str(lane): {
                "total": sum(x["worker"] == lane for x in rows),
                "manual": sum(x["worker"] == lane and
                              x["split_status"] != "mechanical_suggestion" for x in rows),
                "suggested": sum(x["worker"] == lane and
                                 x["split_status"] == "mechanical_suggestion" for x in rows),
            } for lane in range(1, TOTAL_LANES + 1)
        },
        "published": 0, "proofs_reviewed": 0,
        "note": "Machine extraction and syntax splits are not authoritative Phase 2 reviews.",
    }
    (output / "REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--lane", type=int, choices=[1, 2, 3, 4])
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--merge", action="store_true")
    p.add_argument("--delay", type=float, default=0.15)
    p.add_argument("--limit", type=int, default=0)
    o = p.parse_args()
    if o.merge:
        merge(o.input, o.output / "lanes", o.output / "work/wikipedia-stage-a/20261103")
    elif o.lane:
        lane_run(o.input, o.lane, o.output, o.delay, o.limit)
    else:
        p.error("Specify --lane or --merge")


if __name__ == "__main__":
    main()

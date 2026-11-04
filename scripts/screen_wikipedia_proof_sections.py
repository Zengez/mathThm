#!/usr/bin/env python3
"""Wikipedia proof-section *presence* check, not proof validity or completeness.

For each prepared Wikipedia theorem, open an actual proof-labelled section
from MediaWiki. Accept if the section visibly contains nontrivial argument-like
prose/mathematics. Do not check the argument, theorem equivalence, or correctness.
Results preserve all original candidate IDs and all negative/uncertain cases.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlencode, urlsplit
from urllib.request import Request, urlopen

BATCH = "20261104"
LANES = 4
DATE = "2026-11-04"
USER_AGENT = "mathThm-Wikipedia-StructuralProofScreen/1.0 (https://github.com/Zengez/mathThm)"
SOURCE = Path("work/wikipedia-existing-match/20261104/unmatched_prepared.jsonl")
OUT = Path("work/wikipedia-proof-screen/20261104")
VOID = {"br", "hr", "img", "input", "meta", "link", "wbr", "area", "source"}
SKIP = {"script", "style", "table", "nav", "figure", "noscript"}
ARGUMENT = re.compile(
    r"\b(?:thus|hence|therefore|because|since|it follows|we (?:have|obtain|"
    r"show|prove|deduce|conclude|write|use|compute)|suppose|assume|consider|"
    r"observe|let|then|so|by (?:the|a|an)|applying|induction|implies|"
    r"substitut\w*|integrat\w*|differentiat\w*|equalit\w*|inequalit\w*|"
    r"consequent\w*|follows from)\b", re.I)
EMPTY_REF = re.compile(
    r"(?:proof (?:is|was|will be) (?:omitted|not (?:shown|given|included)|left)|"
    r"no proof (?:is|was) (?:known|included|given)|"
    r"see .{0,80} (?:for (?:the |a )?proof|for details)|"
    r"(?:the |a )?proof (?:can be found|is given|is available|appears) (?:in|elsewhere))",
    re.I)


def title_from_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.netloc != "en.wikipedia.org" or not parsed.path.startswith("/wiki/"):
        raise ValueError("Not an English Wikipedia article URL: " + url)
    return unquote(parsed.path.split("/wiki/", 1)[1]).replace("_", " ")


def cleanup(value: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]*>", " ", value or "")).split())


def is_proof_heading(name: str) -> bool:
    s = cleanup(name).casefold().strip(" :.—–")
    if len(s) > 150:
        return False
    if re.search(r"\bproofs?\b", s):
        # Exclude obvious headings about existence/lack of a proof.
        if re.search(r"^(?:history|status|references|search for|unsolved|open problems)", s):
            return False
        return True
    return bool(re.search(r"\b(?:demonstration|proof sketch|sketch of (?:the )?proof)\b", s))


def get_json(page: str, prop: str, section: str | None = None) -> dict:
    query = {"action": "parse", "page": page, "prop": prop,
             "format": "json", "formatversion": "2"}
    if section is not None:
        query["section"] = str(section)
    url = "https://en.wikipedia.org/w/api.php?" + urlencode(query)
    last_exc = None
    for attempt in range(3):
        try:
            req = Request(url, headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            })
            with urlopen(req, timeout=21) as response:
                raw = response.read(5_000_001)
            if len(raw) > 5_000_000:
                raise ValueError("Response exceeds 5 MB")
            parsed = json.loads(raw)
            if "error" in parsed or "parse" not in parsed:
                raise ValueError(str(parsed.get("error") or "Missing parse result")[:260])
            return parsed["parse"]
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            last_exc = exc
            if isinstance(exc, HTTPError) and exc.code in (400, 403, 404):
                break
            if attempt < 2:
                time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(type(last_exc).__name__ + ": " + str(last_exc)[:250])


class SectionText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.math_count = 0
        self.math_characters = 0
        self.paragraphs = 0
        self.list_items = 0
        self.skip_depth = 0
        self.math_depth = 0

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if self.skip_depth:
            if tag not in VOID:
                self.skip_depth += 1
            return
        css = props.get("class", "")
        if tag in SKIP or (
            tag in ("sup", "div", "span") and any(z in css for z in (
                "reference", "mw-editsection", "navbox", "infobox",
                "mw-cite-backlink", "metadata", "toc", "hatnote"))):
            self.skip_depth = 1
            return
        if tag == "math":
            self.math_depth += 1
            if self.math_depth == 1:
                tex = unescape(props.get("alttext", "")).strip()
                if tex:
                    self.math_count += 1
                    self.math_characters += len(tex)
                    self.parts.append(" [mathematical expression] ")
            return
        if tag == "p":
            self.paragraphs += 1
        elif tag == "li":
            self.list_items += 1
        if tag in ("p", "li", "br", "div", "dd", "dt"):
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "math" and self.math_depth:
            self.math_depth -= 1
        elif tag in ("p", "li", "div", "dd"):
            self.parts.append(" ")

    def handle_data(self, data):
        if not self.skip_depth and not self.math_depth:
            self.parts.append(data)

    def stats(self) -> dict:
        text = " ".join(" ".join(self.parts).split())
        prose = text.replace("[mathematical expression]", " ")
        words = re.findall(r"\b[\w'-]+\b", prose, flags=re.UNICODE)
        return {
            "word_count": len(words),
            "text_characters": len(prose),
            "paragraph_count": self.paragraphs,
            "list_item_count": self.list_items,
            "math_count": self.math_count,
            "math_characters": self.math_characters,
            "argument_cues": len(ARGUMENT.findall(prose[:16000])),
            "reference_only_cue": bool(EMPTY_REF.search(prose[:1500])),
            "excerpt": prose[:220].strip(),
        }


def screen_stats(st: dict) -> tuple[bool, str]:
    w, math_ct, math_chars = st["word_count"], st["math_count"], st["math_characters"]
    argument = st["argument_cues"]
    if st["reference_only_cue"] and w < 75 and math_ct < 2:
        return False, "proof_refers_elsewhere_or_is_omitted"
    # Deliberately permissive: this is *evidence of a proof-looking section*,
    # not a minimum length, theorem relevance, or mathematical validity test.
    if w >= 28 and argument:
        return True, "argument_like_prose"
    if math_ct >= 1 and w >= 12 and (
            argument or math_chars >= 20 or math_ct >= 2):
        return True, "prose_and_mathematical_expression"
    if math_ct >= 2 and math_chars >= 45:
        return True, "multi_expression_argument"
    if w >= 75 and (st["paragraph_count"] >= 1 or st["list_item_count"] >= 1):
        return True, "substantive_proof_section_prose"
    if w >= 20 and argument and (math_ct or st["list_item_count"] >= 2):
        return True, "short_argument_with_structure"
    return False, "section_too_thin_or_uninformative"


def screen_one(candidate: dict) -> dict:
    source = candidate["url"]
    result = {
        "candidate_id": candidate["candidate_id"], "url": source,
        "title": candidate["title"], "input_index": candidate["input_index"],
        "status": "inconclusive", "reason": "not_checked",
        "proof_url": None, "proof_heading": None,
        "proof_section_index": None, "section_stats": None,
        "inspection_date": DATE, "screening_scope": "structure_only_not_validity_or_completeness",
    }
    try:
        page = title_from_url(source)
        sections = get_json(page, "sections").get("sections") or []
        proof_sections = [s for s in sections if is_proof_heading(s.get("line", ""))]
        if not proof_sections:
            result.update(status="no_visible_proof", reason="no_proof_labeled_section")
            return result

        seen = []
        problems = []
        for item in proof_sections[:5]:
            idx = item.get("index")
            anchor = item.get("anchor") or ""
            if not idx or not anchor:
                problems.append("section_lacks_index_or_anchor")
                continue
            try:
                section = get_json(page, "text", str(idx))
                html = section.get("text")
                if not isinstance(html, str):
                    problems.append("section_has_no_html")
                    continue
                parser = SectionText()
                parser.feed(html[:1_200_000])
                st = parser.stats()
                good, why = screen_stats(st)
                seen.append({
                    "section_index": str(idx), "heading": cleanup(item.get("line", "")),
                    "anchor": anchor, "stats": st, "passes": good, "reason": why,
                })
                if good:
                    result.update(status="appears_to_contain_proof",
                        reason=why, proof_heading=cleanup(item.get("line", "")),
                        proof_section_index=str(idx), section_stats=st,
                        proof_url=source.split("#", 1)[0] + "#" + quote(anchor, safe=":-._"))
                    return result
            except RuntimeError as exc:
                problems.append(str(exc)[:220])
        if seen:
            best = max(seen, key=lambda x: (
                x["stats"]["word_count"] + 10*x["stats"]["math_count"], -len(x["heading"])))
            result.update(status="no_visible_proof", reason=best["reason"],
                          proof_heading=best["heading"], proof_section_index=best["section_index"],
                          section_stats=best["stats"],
                          proof_url=source.split("#", 1)[0] + "#" + quote(best["anchor"], safe=":-._"))
        else:
            result.update(status="inconclusive", reason="unable_to_read_proof_section")
        if problems:
            result["fetch_notes"] = problems[:5]
    except RuntimeError as exc:
        result.update(status="inconclusive", reason="page_or_section_fetch_failure",
                      fetch_notes=[str(exc)[:240]])
    return result


def read_candidates(path: Path) -> list[dict]:
    rows = [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines() if s.strip()]
    if len(rows) != 984:
        raise ValueError("Expected 984 prepared, unmatched Wikipedia candidates")
    ids = [r["candidate_id"] for r in rows]
    if len(ids) != len(set(ids)) or not all(
            r.get("status") == "standalone_prepared" for r in rows):
        raise ValueError("Candidates have duplicate IDs or unexpected editorial status")
    return rows


def dump_jsonl(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                            for r in rows), encoding="utf-8")


def lane_run(source: Path, lane: int, output: Path, delay: float = .1, limit: int = 0):
    rows = [c for i,c in enumerate(read_candidates(source)) if i % LANES == lane - 1]
    if limit:
        rows = rows[:limit]
    output.mkdir(parents=True, exist_ok=True)
    decisions = []
    for k, candidate in enumerate(rows, 1):
        decisions.append(screen_one(candidate))
        if k % 30 == 0:
            dump_jsonl(output / f"lane-{lane}.jsonl", decisions)
            print(f"Lane {lane}: {k}/{len(rows)} checked, "
                  f"{dict(Counter(d['status'] for d in decisions))}", flush=True)
        if delay:
            time.sleep(delay)
    dump_jsonl(output / f"lane-{lane}.jsonl", decisions)
    print(f"Lane {lane} complete: {dict(Counter(d['status'] for d in decisions))}",flush=True)


def combine(source: Path, lane_dir: Path, output: Path):
    candidates = read_candidates(source)
    expected = {r["candidate_id"]: r for r in candidates}
    decisions = {}
    for lane in range(1, LANES+1):
        path = lane_dir / f"lane-{lane}.jsonl"
        if not path.exists():
            raise ValueError(f"Missing lane {lane}")
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        assigned = {r["candidate_id"] for i,r in enumerate(candidates) if i % LANES == lane-1}
        if {r["candidate_id"] for r in rows} != assigned or len(rows) != len(assigned):
            raise ValueError(f"Lane {lane} missing, unexpected, or duplicate candidate IDs")
        for d in rows:
            src = expected[d["candidate_id"]]
            if d["url"] != src["url"] or d["input_index"] != src["input_index"]:
                raise ValueError("Screening changed original candidate identity")
            if d["status"] not in ("appears_to_contain_proof","no_visible_proof","inconclusive"):
                raise ValueError("Invalid structural screening status")
            if d["status"] == "appears_to_contain_proof" and not d["proof_url"]:
                raise ValueError("Pass without actual proof section URL")
            decisions[d["candidate_id"]] = d

    ordered = [decisions[c["candidate_id"]] for c in candidates]
    passed=[]; held=[]
    for c,d in zip(candidates,ordered):
        enriched = dict(c)
        enriched["proof_screening"] = d
        if d["status"] == "appears_to_contain_proof":
            enriched["proofs"] = [{
                "url": d["proof_url"],
                "locator": d["proof_heading"],
                "screening": "cursory_screened",
                "accessed_on": d["inspection_date"],
                "screening_scope": d["screening_scope"],
                "screening_basis": d["reason"],
            }]
            enriched["acquisition"] = {
                "status": "cursory_screened",
                "batch_id": "wikipedia-structural-proof-20261104",
                "collected_on": DATE,
            }
            passed.append(enriched)
        else:
            enriched["proof_candidates"] = ([{
                "url": d["proof_url"],"status":"uninspected_or_empty",
                "reason":d["reason"],
            }] if d["proof_url"] else [])
            held.append(enriched)
    counts = Counter(d["status"] for d in ordered)
    reasons = Counter(d["reason"] for d in ordered)
    output.mkdir(parents=True,exist_ok=True)
    dump_jsonl(output/"decisions.jsonl",ordered)
    dump_jsonl(output/"proof_screened_candidates.jsonl",passed)
    dump_jsonl(output/"held_proof_sections.jsonl",held)
    (output/"proof_screened_urls.txt").write_text(
        "\n".join(c["url"] for c in passed)+"\n",encoding="utf-8")
    report = {
        "schema":"maththm.wikipedia-structural-proof-screen.v1",
        "prepared_candidates_checked":len(candidates),
        "screened_with_proof_looking_content":len(passed),
        "held_without_visible_proof":len(held),
        "status_counts":dict(sorted(counts.items())),
        "reason_counts":dict(sorted(reasons.items())),
        "previous_source_clarity_holds_unchanged":137,
        "actual_proof_validity_checked":False,
        "proof_completeness_checked":False,
        "new_theorems_published":0,
        "scope":"Visible proof-labeled section with mathematical/argument-like content, not proof verification",
    }
    (output/"REPORT.json").write_text(
        json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,default=SOURCE)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--lane",type=int,choices=range(1,LANES+1))
    parser.add_argument("--combine",action="store_true")
    parser.add_argument("--lane-dir",type=Path)
    parser.add_argument("--limit",type=int,default=0)
    parser.add_argument("--delay",type=float,default=.1)
    options=parser.parse_args()
    if options.combine:
        if not options.lane_dir:
            parser.error("--combine requires --lane-dir")
        combine(options.input,options.lane_dir,options.output)
    elif options.lane:
        lane_run(options.input,options.lane,options.output,options.delay,options.limit)
    else:
        parser.error("Specify --lane or --combine")


if __name__=="__main__":
    main()

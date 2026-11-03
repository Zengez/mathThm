#!/usr/bin/env python3
"""Fast high-recall file/line scan for Stacks standing context; no interpretation."""
from __future__ import annotations
import argparse
import bisect
import json
import re
from collections import Counter
from pathlib import Path

REV = "a04446e57ec1fbc252a871afcec7752fb2807b14"
URL = "https://github.com/stacks/stacks-project/blob/" + REV + "/"
PREFIX = "stacks_context_recon_2026-10-28"
TITLE = re.compile(r"\\title\{([^}\n]+)\}")
SECTION = re.compile(r"\\section(?:\[[^\]\n]*\])?\{([^}\n]+)\}")
LABEL = re.compile(r"\\label\{([^}\n]+)\}")
CONTEXT_HEADING = re.compile(
    r"(?i)conventions?|assumptions?|notation|terminolog|preliminar|"
    r"set.?up|framework|standing|abuse of language|hypotheses"
)
STRONG = {
    "standing": re.compile(r"(?i)\bstanding\s+(?:assumption|hypoth|convention)"),
    "convention": re.compile(r"(?i)\b(?:our|the|these|same|previous|following)\s+conventions?\b"
                             r"|\b(?:follow|adopt|retain)\s+(?:the\s+)?conventions?\b"),
    "broad_scope": re.compile(r"(?i)\bthroughout\b|\bfor\s+the\s+(?:rest|remainder)\s+of\b"
                               r"|\bin\s+the\s+sequel\b|\bhenceforth\b|\bhereafter\b"),
    "exceptions": re.compile(r"(?i)\bunless\s+(?:otherwise|explicitly|stated)\b"
                              r"|\bno\s+longer\s+assume\b"),
    "assume_fix": re.compile(r"(?i)\bwe\s+(?:will\s+|shall\s+|always\s+)?"
                              r"(?:assume|fix|work\s+with)\b"
                              r"|\blet\s+.{3,120}\s+be\s+fixed\b"),
    "chapter_section": re.compile(r"(?i)\bin\s+this\s+(?:chapter|section)\s+"
                                   r"(?:we|the|our|all)\b"
                                   r"|\bfor\s+(?:this|the)\s+(?:chapter|section)\b"),
    "inherited_setup": re.compile(r"(?i)\b(?:continue|retain|use)\s+"
                                   r"(?:to\s+use\s+)?(?:the\s+)?"
                                   r"(?:notation|convention|assumption)"),
}
WEAK = {
    "notation_use": re.compile(r"(?i)\bwe\s+(?:will\s+|shall\s+)?(?:write|denote|call|use)\b"),
    "fixed_choice": re.compile(r"(?i)\bwe\s+(?:choose|take|pick)\b|\bfix\s+(?:a|an|the)\b"),
}

def ordered_chapters(root):
    items = []
    taking = False
    for line in (root / "Makefile").read_text().splitlines():
        if line.startswith("LIJST = "):
            line = line.split("=", 1)[1]
            taking = True
        if taking:
            items.extend(line.strip().removesuffix("\\").split())
            if not line.rstrip().endswith("\\"):
                break
    assert len(items) >= 100 and len(set(items)) == len(items)
    return items

def book_parts(root):
    result = {}
    lines = (root / "chapters.tex").read_text().splitlines()
    part = ""
    for i, line in enumerate(lines):
        if (i + 1 < len(lines) and lines[i + 1].strip() == r"\begin{enumerate}"
                and line.strip() and not line.lstrip().startswith("\\")):
            part = line.strip()
        m = re.search(r"\\hyperref\[([a-z-]+)-section-phantom\]", line)
        if m:
            result[m.group(1)] = part
    return result

def file_scan(path, order, parts):
    lines = path.read_text(encoding="utf-8").splitlines()
    m = TITLE.search("\n".join(lines[:35]))
    title = m.group(1) if m else path.stem
    starts = []
    sections = []
    for i, line in enumerate(lines, 1):
        h = SECTION.search(line)
        if not h:
            continue
        label = None
        for following in lines[i:min(i + 3, len(lines))]:
            ml = LABEL.search(following)
            if ml:
                label = ml.group(1)
                break
        sections.append({"line": i, "title": h.group(1), "label": label})
        starts.append(i)
    headings = [
        {"line": s["line"], "title": s["title"], "label": s["label"],
         "url": URL + path.name + "#L" + str(s["line"])}
        for s in sections if CONTEXT_HEADING.search(s["title"])
    ]
    counts = Counter()
    strong = []
    weak = []
    in_proof = False
    next_boundary = {}
    for k, section in enumerate(sections):
        end = sections[k + 1]["line"] if k + 1 < len(sections) else len(lines) + 1
        first_env = end
        for i in range(section["line"], end):
            if re.search(r"\\begin\{(?:lemma|theorem|corollary|proposition|"
                         r"definition|situation|notation|proof|remark|example|construction)\}", lines[i - 1]):
                first_env = i
                break
        next_boundary[k] = first_env
    for i, line in enumerate(lines, 1):
        if r"\begin{proof}" in line:
            in_proof = True
        if in_proof:
            if r"\end{proof}" in line:
                in_proof = False
            continue
        if not line.strip() or line.lstrip().startswith("%"):
            continue
        section_idx = bisect.bisect_right(starts, i) - 1
        section = sections[section_idx] if section_idx >= 0 else None
        strong_hits = [k for k, pat in STRONG.items() if pat.search(line)]
        weak_hits = [k for k, pat in WEAK.items() if pat.search(line)]
        if not strong_hits and not weak_hits:
            continue
        for k in (strong_hits or weak_hits):
            counts[k] += 1
        row = {
            "line": i, "section": section["title"] if section else None,
            "section_label": section["label"] if section else None,
            "in_section_opening": bool(section and i < next_boundary[section_idx]),
            "signals": strong_hits or weak_hits,
            "snippet": line.strip()[:180],
            "url": URL + path.name + "#L" + str(i),
        }
        (strong if strong_hits else weak).append(row)
    strong.sort(key=lambda x: (not x["in_section_opening"], x["line"] > 400, x["line"]))
    weak.sort(key=lambda x: (not x["in_section_opening"], x["line"]))
    samples = (strong + weak)[:8]
    score = (
        int(path.name == "conventions.tex") * 100 +
        min(len(headings), 8) * 8 +
        min(len(strong), 16) * 2 +
        min(sum(x["in_section_opening"] for x in strong), 10) * 3 +
        min(len(weak), 10)
    )
    return {
        "filename": path.name,
        "chapter_number": order.get(path.stem),
        "book_part": parts.get(path.stem),
        "title": title,
        "in_main_book_order": path.stem in order,
        "is_global_conventions": path.name == "conventions.tex",
        "source_revision": REV,
        "file_bytes": path.stat().st_size,
        "total_lines": len(lines),
        "section_count": len(sections),
        "context_heading_leads": headings,
        "context_heading_count": len(headings),
        "strong_phrase_leads": len(strong),
        "soft_phrase_leads": len(weak),
        "signals_by_kind": dict(sorted(counts.items())),
        "sample_phrase_leads": samples,
        "priority_score": score,
        "lead_only_no_scope_or_semantic_assessment": True,
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", default="upstream/stacks")
    ap.add_argument("--output-dir", default="harvest")
    args = ap.parse_args()
    root = Path(args.source_root)
    out = Path(args.output_dir)
    if not (root / "Makefile").is_file() or not (root / "conventions.tex").is_file():
        raise FileNotFoundError("Complete pinned Stacks source checkout required")
    chapters = ordered_chapters(root)
    order = {stem: i + 1 for i, stem in enumerate(chapters)}
    parts = book_parts(root)
    all_files = sorted(root.glob("*.tex"))
    assert all((root / (stem + ".tex")).exists() for stem in chapters)
    reports = sorted(
        [file_scan(p, order, parts) for p in all_files],
        key=lambda x: (-x["priority_score"], x["chapter_number"] or 999, x["filename"])
    )
    summary = {
        "schema": "maththm.stacks-context-recon.v1",
        "source_revision": REV,
        "source_files_scanned": len(reports),
        "main_book_chapters": len(chapters),
        "files_with_context_headings": sum(x["context_heading_count"] > 0 for x in reports),
        "files_with_strong_phrases": sum(x["strong_phrase_leads"] > 0 for x in reports),
        "files_with_strong_phrases_or_headings": sum(
            x["strong_phrase_leads"] > 0 or x["context_heading_count"] > 0 for x in reports
        ),
        "heading_leads": sum(x["context_heading_count"] for x in reports),
        "strong_phrase_occurrences": sum(x["strong_phrase_leads"] for x in reports),
        "soft_phrase_occurrences": sum(x["soft_phrase_leads"] for x in reports),
        "all_files_report": PREFIX + "_files.jsonl",
        "priority_report": PREFIX + "_priority.md",
        "method": "Whole-file quick regex reconnaissance; proof bodies skipped; headings and phrase hits only",
        "scope_inferred": False,
        "mathematical_context_interpreted": False,
        "candidate_hypotheses_modified": False,
        "theorem_proofs_reviewed": False,
        "false_positive_tolerance": "high",
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / (PREFIX + "_files.jsonl")).write_text(
        "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in reports),
        encoding="utf-8",
    )
    (out / (PREFIX + "_manifest.json")).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    md = [
        "# Stacks convention/standing-context reconnaissance",
        "",
        "Pinned revision: " + REV,
        "",
        "This is a **high-recall list of file and line leads**, not a mathematical context extraction.",
        "Chapter order is taken from the maintained Stacks Makefile. It does not imply assumptions accumulate across chapters.",
        "",
        f"Scanned **{len(reports)}** LaTeX files ({len(chapters)} ordered book chapters).",
        f"Found **{summary['files_with_strong_phrases_or_headings']}** files with strong phrases or explicitly context-like headings.",
        f"Flagged **{summary['heading_leads']}** context-like headings, **{summary['strong_phrase_occurrences']}** strong phrase occurrences, and **{summary['soft_phrase_occurrences']}** weaker phrase occurrences.",
        "",
        "## Highest-priority files for later closer reading",
        "",
        "| Book order | File | Context headings | Strong phrases | Sections | Example context headings |",
        "|---:|---|---:|---:|---:|---|",
    ]
    for row in reports[:55]:
        head = "; ".join(x["title"].replace("|", " ") for x in row["context_heading_leads"][:3])
        num = row["chapter_number"] if row["chapter_number"] else "—"
        md.append(
            f"| {num} | [{row['filename']}]({URL}{row['filename']}) | "
            f"{row['context_heading_count']} | {row['strong_phrase_leads']} | "
            f"{row['section_count']} | {head[:110]} |"
        )
    md.extend([
        "",
        "## Deferred work (not part of this scan)",
        "",
        "1. Read flagged global and chapter-wide convention candidates and determine their actual scope.",
        "2. Extract chapter and section opening context as a separate, small indexed resource.",
        "3. For each candidate theorem, resolve only the missing inherited references and local assumptions.",
        "",
        "No hypotheses, canonically deduplicated records, published theorems, or proofs were modified.",
        "",
    ])
    (out / (PREFIX + "_priority.md")).write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in (
        "source_files_scanned", "main_book_chapters",
        "files_with_strong_phrases_or_headings", "heading_leads",
        "strong_phrase_occurrences", "soft_phrase_occurrences"
    )}, sort_keys=True))

if __name__ == "__main__":
    main()

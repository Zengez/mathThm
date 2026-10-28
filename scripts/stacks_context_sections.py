#!/usr/bin/env python3
"""Bounded pinned Stacks convention/notation sections for human review.

Intentionally no mathematical interpretation and no theorem updates.
Extract only designated sections and the global Conventions chapter,
with explicit source locators. Never read proof bodies.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from collections import Counter
from scripts.stacks_context_recon import REV, URL, ordered_chapters, book_parts, SECTION

LABEL = re.compile(r"\\label\{([^}\n]+)\}")
HEADING = re.compile(r"(?i)conventions?|notation|set.?up|standing|assumptions?|abuse of language")
PROOF = re.compile(r"\\begin\{proof\}[\s\S]*?\\end\{proof\}", re.I)
MATH_ENV = re.compile(r"\\begin\{(lemma|proposition|theorem|corollary|definition|situation|construction|remark)\}")
EXPLICIT = re.compile(r"\\ref\{([^}\n]+)\}")
BASE = "harvest/stacks_context_sections_2026-10-28"

def extract(root, out):
    order = {stem: i + 1 for i, stem in enumerate(ordered_chapters(root))}
    parts = book_parts(root)
    sections = []
    for stem, number in sorted(order.items(), key=lambda kv: kv[1]):
        path = root / (stem + ".tex")
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        heads = [(i, m.group(1)) for i, line in enumerate(lines, 1)
                 if (m := SECTION.search(line))]
        name_match = re.search(r"\\title\{([^}\n]+)\}", "\n".join(lines[:40]))
        title = name_match.group(1) if name_match else stem
        for ix, (start, heading) in enumerate(heads):
            if stem != "conventions" and not HEADING.search(heading):
                continue
            end = heads[ix + 1][0] - 1 if ix + 1 < len(heads) else len(lines)
            subsection_text = "\n".join(lines[start:end])
            labelmatch = LABEL.search("\n".join(lines[start:start + 3]))
            label = labelmatch.group(1) if labelmatch else None
            without_proof = PROOF.sub("\n[PROOF OMITTED]\n", subsection_text)
            # Some sections have no proof but still very long content. Preserve
            # only short review excerpts. The full source remains linked.
            excerpt = without_proof[:6500]
            sections.append({
                "context_id": stem + ":" + (label or "line-" + str(start)),
                "filename": path.name,
                "chapter_title": title,
                "book_part": parts.get(stem),
                "chapter_number": number,
                "section_title": heading,
                "section_label": label,
                "first_line": start,
                "last_line": end,
                "source_revision": REV,
                "source_url": URL + path.name + "#L" + str(start),
                "source_line_count": end-start+1,
                "review_excerpt": excerpt.strip(),
                "source_chars_excluding_proofs": len(without_proof),
                "excerpt_truncated": len(without_proof) > 6500,
                "proof_blocks_omitted": subsection_text.count(r"\begin{proof}"),
                "references": list(dict.fromkeys(EXPLICIT.findall(excerpt)))[:25],
                "formal_environments_in_excerpt": sorted(set(MATH_ENV.findall(excerpt))),
                "status": "review_packet_not_an_assertion",
            })
    out.mkdir(parents=True, exist_ok=True)
    target=out/"stacks_context_sections_2026-10-28_packets.jsonl"
    target.write_text("".join(json.dumps(x, ensure_ascii=False, sort_keys=True)+"\n" for x in sections), encoding="utf-8")
    summary={
        "schema":"maththm.stacks-context-section-packets.v1",
        "source_revision":REV,
        "section_packets":len(sections),
        "chapters_represented":len({x["filename"] for x in sections}),
        "conventions_chapter_sections":sum(x["filename"]=="conventions.tex" for x in sections),
        "other_designated_sections":sum(x["filename"]!="conventions.tex" for x in sections),
        "truncated_excerpts":sum(x["excerpt_truncated"] for x in sections),
        "sections_with_proofs_omitted":sum(x["proof_blocks_omitted"]>0 for x in sections),
        "packets_file":target.name,
        "no_scope_or_mathematical_interpretation":True,
        "no_candidate_edits":True,
    }
    (out/"stacks_context_sections_2026-10-28_manifest.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(summary,sort_keys=True))
    return summary

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",default="upstream/stacks")
    ap.add_argument("--output-dir",default="harvest")
    args=ap.parse_args()
    extract(Path(args.source_root),Path(args.output_dir))

if __name__=="__main__":
    main()

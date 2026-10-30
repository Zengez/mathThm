#!/usr/bin/env python3
"""Mechanical, proof-free, per-chapter Stage A review inputs.

This prepares source/context evidence, never mathematical equivalence, review
decisions, or Phase 3 eligibility. After a completed Codex review batch,
remove approved candidates from the existing prepared files once rather
than adding skip/status lookups to normal section processing.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from scripts import stacks_section_walk_pilot as walk
from scripts.harvest_pipeline import atomic_text
from scripts.stacks_context_recon import REV

DEFAULT_OUT = Path("harvest/phase2_prepared") / REV[:12]
PROOF_TOKEN = re.compile(r"\\(begin|end)\{proof\}")


def json_line(row):
    return json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"


def proof_free_lines(lines, first=1, last=None):
    """Yield numbered TeX lines with proof bodies omitted, preserving positions.

    Reject unbalanced proof markers rather than providing potentially leaked
    proof text. Keep source outside same-line proof boundaries.
    """
    last = len(lines) if last is None else last
    if not (1 <= first <= last + 1 <= len(lines) + 1):
        raise ValueError("Invalid source line interval")
    inside = False
    result = []
    omitted = 0
    for no in range(first, last + 1):
        line = walk.without_comments(lines[no - 1])
        bits = []
        pos = 0
        had_proof = inside
        for match in PROOF_TOKEN.finditer(line):
            kind = match.group(1)
            if kind == "begin":
                if inside:
                    raise ValueError(f"Nested proof at source line {no}")
                bits.append(line[pos:match.start()])
                inside = True
            else:
                if not inside:
                    raise ValueError(f"Proof ended without begin at line {no}")
                inside = False
            pos = match.end()
            had_proof = True
        if not inside:
            bits.append(line[pos:])
        visible = "".join(bits)
        if had_proof:
            omitted += 1
        if visible.strip():
            result.append({"line": no, "tex": visible})
    if inside:
        raise ValueError("Unclosed proof in source interval")
    return result, omitted


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def existing_draft_sections():
    path = Path("harvest/SECTION_WALK_COMPLETED_SECTIONS.json")
    if not path.is_file():
        return {}
    registry = json.loads(path.read_text(encoding="utf-8"))
    if registry["source_revision"] != REV:
        raise ValueError("Draft-section registry uses another Stacks revision")
    return {(r["source_file"], r["section_start_line"]): r["artifacts"]
            for r in registry["sections"]}


def chapter_inventory():
    grouped, byfile, unmatched = walk.groups()
    if unmatched:
        raise ValueError(f"Active candidates outside indexed sections: {len(unmatched)}")
    chapters = sorted(byfile, key=lambda name: (byfile[name][0]["chapter_number"], name))
    seen = [c[0] for section in grouped.values() for c in section]
    if len(seen) != 9675 or len(set(seen)) != len(seen):
        raise ValueError("Canonical active population differs from 9,675 unique IDs")
    return grouped, byfile, chapters


def selected(chapters, requested, missing_only, out, limit):
    if requested.strip().lower() == "all":
        names = list(chapters)
    else:
        names = [p.strip() for p in requested.split(",") if p.strip()]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate chapter request")
        unknown = set(names) - set(chapters)
        if unknown:
            raise ValueError(f"Unknown Stacks chapters: {sorted(unknown)}")
        names.sort(key=chapters.index)
    if missing_only:
        names = [name for name in names if not (out / Path(name).stem / "MANIFEST.json").exists()]
    if limit > 0:
        names = names[:limit]
    return names


def prepare_one(source_root, out, chapter, sections, grouped, drafts):
    source = source_root / chapter
    if not source.is_file():
        raise FileNotFoundError(f"Pinned Stacks chapter unavailable: {source}")
    lines = source.read_text(encoding="utf-8").splitlines()
    dest = out / Path(chapter).stem
    expected = dest / "MANIFEST.json"
    if expected.exists():
        previous = json.loads(expected.read_text(encoding="utf-8"))
        if previous.get("source_revision") != REV or previous.get("source_file") != chapter:
            raise ValueError("Existing chapter preparation is incompatible; do not overwrite")
    for a, b in zip(sections, sections[1:]):
        if a["section_end_line"] + 1 != b["section_start_line"]:
            raise ValueError(f"Nonconsecutive section boundaries in {chapter}")
    preamble, preproof = proof_free_lines(lines, 1, sections[0]["section_start_line"] - 1)
    section_rows = []
    candidate_rows = []
    omitted_proof_lines = preproof
    scope_issues = 0
    for section in sections:
        first, last = section["section_start_line"], section["section_end_line"]
        if last > len(lines):
            raise ValueError(f"Section exceeds pinned source: {chapter}:{last}")
        members = sorted(grouped.get((chapter, first), []),
                         key=lambda x: (x[1]["source"]["statement_line"], x[0]))
        visible, omitted = proof_free_lines(lines, first, last)
        omitted_proof_lines += omitted
        scope_error = None
        try:
            events, candidates, definitions = walk.walk_events(
                lines, section, {raw["source"]["statement_line"] for _, raw, _ in members})
        except ValueError as exc:
            # Conservative extraction failure is review evidence, not a reason
            # to silently drop a section or candidate.
            events, candidates, definitions = [], [], []
            scope_error = str(exc)
            scope_issues += 1
        artifact = drafts.get((chapter, first))
        section_rows.append({
            "schema": "maththm.phase2.chapter-section-input.v1",
            "source_revision": REV, "source_file": chapter,
            "chapter_number": section["chapter_number"],
            "section_start_line": first, "section_end_line": last,
            "section_title": section["section_title"],
            "section_label": section["section_label"],
            "proof_free_source_lines": visible,
            "omitted_proof_line_count": omitted,
            "source_scope_events_unadjudicated": events,
            "possible_scope_prose_line_numbers": candidates,
            "locally_named_context_leads": definitions,
            "scope_extraction_error_requires_review": scope_error,
            "previous_draft_artifact_hint": artifact,
            "candidate_ids": [ident for ident, _, _ in members],
            "no_ambient_hypotheses_inferred": True,
        })
        for ident, raw, p2 in members:
            src = raw["source"]
            if src["filename"] != chapter or not first <= src["statement_line"] <= last:
                raise ValueError(f"Source location mismatch for {ident}")
            candidate_rows.append({
                "schema": "maththm.phase2.chapter-candidate-input.v1",
                "candidate_id": ident, "source_revision": REV,
                "source_file": chapter, "source_line": src["statement_line"],
                "source_label": src.get("label"),
                "source_url": src.get("source_url"),
                "section_start_line": first, "section_end_line": last,
                "original_source_statement_tex": raw["statement_tex"],
                "detected_local_references": raw.get("detected_local_references", []),
                "preliminary_pass2": {
                    field: p2[field] for field in (
                        "statement", "hypotheses", "conclusions", "context_status",
                        "context_note", "logical_form", "statement_tex"
                    ) if field in p2
                },
                "previous_draft_artifact_hint": artifact,
                "preparation_only": True,
                "mathematical_source_equivalence_reviewed": False,
                "phase3_eligible": False,
                "proof_reviewed": False,
            })
    ids = [r["candidate_id"] for r in candidate_rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate candidates in {chapter}")
    if len(candidate_rows) != sum(len(grouped.get((chapter, s["section_start_line"]), []))
                                  for s in sections):
        raise ValueError(f"Missing candidates in {chapter}")
    dest.mkdir(parents=True, exist_ok=True)
    atomic_text(dest / "SECTIONS.jsonl", "".join(map(json_line, section_rows)))
    atomic_text(dest / "CANDIDATES.jsonl", "".join(map(json_line, candidate_rows)))
    manifest = {
        "schema": "maththm.phase2.chapter-preparation.v1",
        "source_revision": REV, "source_file": chapter,
        "chapter_number": sections[0]["chapter_number"],
        "chapter_title": sections[0].get("chapter_title", Path(chapter).stem),
        "section_count": len(sections),
        "complete_consecutive_sections": True,
        "candidate_count": len(candidate_rows),
        "candidate_ids_sha256": hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest(),
        "preamble_proof_free_lines": preamble,
        "source_scope_extraction_issues": scope_issues,
        "omitted_proof_line_count": omitted_proof_lines,
        "source_sha256": sha256(source),
        "section_inputs_sha256": sha256(dest / "SECTIONS.jsonl"),
        "candidate_inputs_sha256": sha256(dest / "CANDIDATES.jsonl"),
        "note": "Preliminary source/context evidence only; no mathematical interpretations or approvals.",
        "stage_a_complete": False, "stage_b_complete": False,
        "phase3_eligible": False, "proof_screened": False, "published": False,
    }
    atomic_text(expected, json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return manifest


def update_index(out):
    chapters = []
    for file in sorted(out.glob("*/MANIFEST.json")):
        entry = json.loads(file.read_text(encoding="utf-8"))
        if entry["source_revision"] != REV:
            raise ValueError("Mixed Stacks source revisions in prepared index")
        for name, hashfield in (("SECTIONS.jsonl", "section_inputs_sha256"),
                                ("CANDIDATES.jsonl", "candidate_inputs_sha256")):
            if sha256(file.parent / name) != entry[hashfield]:
                raise ValueError(f"Prepared chapter file hash mismatch: {file.parent / name}")
        chapters.append({
            "source_file": entry["source_file"],
            "chapter_number": entry["chapter_number"],
            "candidate_count": entry["candidate_count"],
            "section_count": entry["section_count"],
            "manifest": str(file),
        })
    chapters.sort(key=lambda r: (r["chapter_number"], r["source_file"]))
    total = sum(r["candidate_count"] for r in chapters)
    atomic_text(out / "INDEX.json", json.dumps({
        "schema": "maththm.phase2.chapter-preparation-index.v1",
        "source_revision": REV,
        "prepared_chapters": len(chapters), "prepared_candidates": total,
        "active_population_expected": 9675,
        "mathematical_approvals_added": 0,
        "preparation_only": True, "chapters": chapters,
    }, indent=2, ensure_ascii=False) + "\n")
    return len(chapters), total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path("upstream/stacks"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--chapters", default="all",
                        help="'all' or comma-separated Stacks *.tex chapter filenames")
    parser.add_argument("--max-chapters", type=int, default=0,
                        help="0 means no limit")
    parser.add_argument("--only-missing", action="store_true")
    parser.add_argument("--list-only", action="store_true",
                        help="print chapter filenames, one per line; no output changes")
    args = parser.parse_args()
    if args.max_chapters < 0:
        parser.error("--max-chapters cannot be negative")
    grouped, byfile, chapters = chapter_inventory()
    names = selected(chapters, args.chapters, args.only_missing, args.output_dir, args.max_chapters)
    if args.list_only:
        for name in names:
            print(name)
        return
    source_head = args.source_root / ".git"
    if not source_head.exists():
        raise ValueError(f"Pinned Stacks checkout missing: {args.source_root}")
    import subprocess
    head = subprocess.check_output(
        ["git", "-C", str(args.source_root), "rev-parse", "HEAD"], text=True).strip()
    if head != REV:
        raise ValueError(f"Stacks source revision mismatch: {head} != {REV}")
    drafts = existing_draft_sections()
    for name in names:
        if (args.output_dir / Path(name).stem / "MANIFEST.json").exists():
            raise ValueError(f"{name} already prepared; use --only-missing to skip")
        manifest = prepare_one(args.source_root, args.output_dir,
                               name, byfile[name], grouped, drafts)
        print(f"PREPARED {name}: {manifest['candidate_count']} candidates, "
              f"{manifest['section_count']} complete sections, "
              f"{manifest['source_scope_extraction_issues']} extraction holds", flush=True)
    count, total = update_index(args.output_dir)
    print(f"INDEX {count} chapters; {total} candidate inputs (no mathematical approvals)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Read-only integrity verification of chapter preparation artifacts.

No content-hash check asserts that hypotheses, conclusions, or mathematics
were validated. This script checks only extraction integrity and provenance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from scripts.phase2_prepare_chapters import DEFAULT_OUT, sha256
from scripts.stacks_context_recon import REV
from scripts.harvest_pipeline import read_jsonl
from scripts import stacks_section_walk_pilot as walk


def verify(root=DEFAULT_OUT, source_root=None):
    root = Path(root)
    index = json.loads((root / "INDEX.json").read_text(encoding="utf-8"))
    if index["source_revision"] != REV or not index["preparation_only"]:
        raise ValueError("Invalid preparation index or source revision")
    manifest_paths = list(root.glob("*/MANIFEST.json"))
    if len(manifest_paths) != index["prepared_chapters"]:
        raise ValueError("Prepared chapter count differs from manifests on disk")
    sections_by_file = walk.section_index()
    all_ids = set()
    total = 0
    for item in index["chapters"]:
        chapter = item["source_file"]
        stem = Path(chapter).stem
        folder = root / stem
        manifest = json.loads((folder / "MANIFEST.json").read_text(encoding="utf-8"))
        if (manifest["source_file"] != chapter or manifest["source_revision"] != REV or
                not manifest["complete_consecutive_sections"] or
                any(manifest[k] for k in ("stage_a_complete", "stage_b_complete",
                                           "phase3_eligible", "proof_screened", "published"))):
            raise ValueError(f"Invalid chapter manifest: {chapter}")
        if source_root is not None and sha256(Path(source_root) / chapter) != manifest["source_sha256"]:
            raise ValueError(f"Source changed: {chapter}")
        for name, field in [("SECTIONS.jsonl", "section_inputs_sha256"),
                            ("CANDIDATES.jsonl", "candidate_inputs_sha256")]:
            if sha256(folder / name) != manifest[field]:
                raise ValueError(f"Prepared input changed: {chapter}/{name}")
        sections = read_jsonl(folder / "SECTIONS.jsonl")
        candidates = read_jsonl(folder / "CANDIDATES.jsonl")
        indexed = sections_by_file[chapter]
        if len(sections) != manifest["section_count"] or len(sections) != len(indexed):
            raise ValueError(f"Not all sections represented: {chapter}")
        if len(candidates) != manifest["candidate_count"] or len(candidates) != item["candidate_count"]:
            raise ValueError(f"Candidate count mismatch: {chapter}")
        actual = [r["candidate_id"] for r in candidates]
        if len(set(actual)) != len(actual):
            raise ValueError(f"Repeated candidate within chapter: {chapter}")
        if all_ids.intersection(actual):
            raise ValueError(f"Candidate appears in multiple prepared chapters: {chapter}")
        all_ids.update(actual)
        digest = hashlib.sha256("\n".join(sorted(actual)).encode()).hexdigest()
        if manifest["candidate_ids_sha256"] != digest:
            raise ValueError(f"Candidate set changed: {chapter}")
        by_section = {}
        for row in candidates:
            if (row["source_revision"] != REV or not row["preparation_only"] or
                    row["phase3_eligible"] or row["mathematical_source_equivalence_reviewed"] or
                    row["proof_reviewed"] or not row["original_source_statement_tex"] or
                    row["source_file"] != chapter):
                raise ValueError(f"Invalid candidate preparation: {row.get('candidate_id')}")
            key = row["section_start_line"]
            by_section.setdefault(key, []).append(row["candidate_id"])
        for prepared, source_section in zip(sections, indexed):
            if (prepared["section_start_line"] != source_section["section_start_line"] or
                    prepared["section_end_line"] != source_section["section_end_line"] or
                    prepared["source_revision"] != REV):
                raise ValueError(f"Section boundary mismatch: {chapter}")
            if sorted(prepared["candidate_ids"]) != sorted(by_section.get(prepared["section_start_line"], [])):
                raise ValueError(f"Section candidate IDs mismatch: {chapter}")
            if not prepared["no_ambient_hypotheses_inferred"]:
                raise ValueError("Inferred ambient hypothesis found")
            prev = prepared["section_start_line"] - 1
            for line in prepared["proof_free_source_lines"]:
                if not prev < line["line"] <= prepared["section_end_line"]:
                    raise ValueError(f"Out-of-order source lines in {chapter}")
                prev = line["line"]
                if r"\begin{proof}" in line["tex"] or r"\end{proof}" in line["tex"]:
                    raise ValueError(f"Proof material exposed: {chapter}")
        total += len(candidates)
    if total != index["prepared_candidates"]:
        raise ValueError("Index and verified candidate totals disagree")
    if total > index["active_population_expected"]:
        raise ValueError("Prepared inputs exceed the canonical active population")
    return {"prepared_chapters": len(index["chapters"]),
            "verified_distinct_candidate_inputs": total, "mathematical_approvals": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--source-root", type=Path, default=None)
    args = parser.parse_args()
    print(json.dumps(verify(args.input_dir, args.source_root), sort_keys=True))


if __name__ == "__main__":
    main()

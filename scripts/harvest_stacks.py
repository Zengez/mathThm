#!/usr/bin/env python3
"""Bounded, non-research Stacks Project LaTeX candidate extractor (Pass 1).

This only detects theorem-like environments followed by an apparent proof.
It NEVER reads a proof for mathematical validity. Candidate records are not
accepted/published theorems. Source files are inputs, never fetched implicitly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

if __package__:
    from .harvest_pipeline import load_rows, merge_rows, save_checkpoint
else:
    from harvest_pipeline import load_rows, merge_rows, save_checkpoint

ENV = re.compile(r"\\begin\{(lemma|theorem|proposition|corollary)\}(?:\[[^\]\n]*\])?\s*"
                 r"([\s\S]*?)\\end\{\1\}", re.IGNORECASE)
PROOF = re.compile(r"^\s*(?:%[^\n]*\n\s*)*\\begin\{proof\}(?:\[[^\]\n]*\])?",
                   re.IGNORECASE)
PROOF_END = re.compile(r"\\end\{proof\}", re.IGNORECASE)
LABEL = re.compile(r"\\label\{([^}]+)\}")
COMMENT = re.compile(r"(?m)^[ \t]*%[^\n]*(?:\n|$)")
REF = re.compile(r"\\ref\{([^}]+)\}")


def line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def discover(text: str, *, filename: str, source_ref: str, batch: str,
             source_id: str = "stacks-project", limit: int = 100000,
             collected_on: str | None = None):
    """Produce source-pinned records, never proof text or an assessment."""
    text = COMMENT.sub("\n", text)
    source_ref = source_ref.strip()
    if not re.fullmatch(r"[0-9a-fA-F]{40}", source_ref):
        raise ValueError("source_ref must be a pinned, full 40-char Git commit SHA")
    if not re.fullmatch(r"[a-zA-Z0-9._/-]+\.tex", filename) or ".." in Path(filename).parts:
        raise ValueError("invalid source filename")
    prefix = "https://github.com/stacks/stacks-project/blob/" + source_ref + "/" + filename
    collected_on = collected_on or date.today().isoformat()
    for match in ENV.finditer(text):
        tail = text[match.end():]
        begin = PROOF.match(tail)
        if not begin:
            continue
        # Anchor the proof URL at the actual proof command, not the newline
        # or whitespace between the result statement and its proof.
        marker = re.search(r"\\begin\{proof\}", tail[:begin.end()], re.IGNORECASE)
        if marker is None:
            continue
        proof_start = match.end() + marker.start()
        end = PROOF_END.search(text, match.end() + begin.end())
        statement = match.group(2).strip()
        if len(statement) < 10:
            continue
        label = LABEL.search(statement)
        # Stable enough to rerun pinned sources; location changes with commit,
        # so source_ref is part of the candidate fingerprint.
        key = f"{source_id}:{source_ref}:{filename}:{label.group(1) if label else match.start()}"
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        first = line(text, match.start())
        proof_line = line(text, proof_start)
        statement_end = line(text, match.end())
        candidate = {
            "candidate_id": "candidate.stacks." + digest,
            "batch_id": batch,
            "entry_type": match.group(1).lower(),
            "title": None,
            "area": "Unclassified",
            "source": {
                "id": source_id,
                "name": "The Stacks Project",
                "attribution": "The Stacks Project Authors",
                "license_note": "GNU Free Documentation License; review attribution and reuse terms before publication",
                "confidence": "established_collaborative_reference",
                "revision": source_ref,
                "filename": filename,
                "source_url": prefix + "#L" + str(first),
                "statement_locator": filename + ":" + str(first) + "-" + str(statement_end),
                "statement_line": first,
                "proof_url": prefix + "#L" + str(proof_line),
                "proof_locator": filename + ":" + str(proof_line) +
                                 ("-" + str(line(text, end.end())) if end else ""),
                "proof_start_line": proof_line,
                "proof_end_line": line(text, end.end()) if end else None,
                "label": label.group(1) if label else None,
            },
            "statement_tex": statement,
            "detected_local_references": REF.findall(statement),
            "proof_marker": "begin_proof_immediately_follows_statement",
            "proof_end_marker_found": end is not None,
            "status": "raw_candidate_unreviewed",
            "collected_on": collected_on,
        }
        yield candidate
        limit -= 1
        if limit <= 0:
            break


def run(args):
    if args.max_candidates_per_file < 1 or args.max_file_bytes < 1:
        raise ValueError("file/candidate bounds must be positive")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    existing = load_rows(out / "pass1.jsonl", "candidate_id")
    added = 0
    file_summaries = {}
    for file in args.files:
        path = Path(file)
        if not path.is_file():
            raise ValueError("source file not found: " + str(path))
        root = Path(args.source_root).resolve()
        try:
            relative = path.resolve().relative_to(root).as_posix()
        except ValueError as ex:
            raise ValueError("source file must reside under --source-root") from ex
        count = 0
        # Bound files before reading large source trees; no recursive crawling.
        if path.stat().st_size > args.max_file_bytes:
            raise ValueError(f"source file too large: {relative}")
        text = path.read_text(encoding="utf-8")
        # Iterate complete file and cap *new* additions, so rerunning with
        # the same bound cannot accidentally add later pages or duplicate rows.
        for c in discover(text, filename=relative, source_ref=args.source_ref,
                          batch=args.batch_id, limit=args.max_candidates_per_file):
            key = c["candidate_id"]
            if key in existing:
                continue
            existing[key] = c
            added += 1
            count += 1
        file_summaries[relative] = count
    merge_rows(out / "pass1.jsonl", existing.values(), "candidate_id")
    save_checkpoint(out)
    print(json.dumps({"stage":"pass1","new_candidates":added,"total_candidates":len(existing),
                      "sources_added":file_summaries}, sort_keys=True))


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", required=True, help="Root directory of pinned Stacks source")
    p.add_argument("--source-ref", required=True, help="40-character Stacks upstream commit SHA")
    p.add_argument("--files", nargs="+", required=True, help="Explicit .tex input paths")
    p.add_argument("--batch-id", required=True)
    p.add_argument("--output-dir", required=True, help="Local work directory, never published by pass 1")
    p.add_argument("--max-candidates-per-file", type=int, default=200)
    p.add_argument("--max-file-bytes", type=int, default=5_000_000)
    return p


if __name__ == "__main__":
    run(parser().parse_args())

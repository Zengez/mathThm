#!/usr/bin/env python3
"""Mechanically correct malformed source-statement digests in Phase 3 proposals.

Only the exact source_statement_sha256 field is changed; candidate IDs,
mathematical content, proof decisions, and authoritative status are immutable.
Operates on the reconciled integration branch, not the original worker heads.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
BASE = "c57a162275ef35a7fe61e87f709627fd98ede4de"
POSITIVE = "source_equivalence_approved_pending_materialization"


def git(*args):
    return subprocess.check_output(("git", *args), cwd=ROOT, text=True).strip()


def rows(path):
    return [json.loads(x) for x in (ROOT / path).read_text(encoding="utf8").splitlines() if x.strip()]


def main():
    fixes = 0
    files = 0
    for worker in range(1, 5):
        queue = json.loads(git("show", f"{BASE}:work/phase3-parallel/worker-{worker}/PENDING.json"))
        for batch in queue["pending"]:
            for section in batch["sections"]:
                source_file = section["file"]
                if git("hash-object", source_file) != section["blob_sha"]:
                    raise ValueError(f"Frozen Stage B blob changed: {source_file}")
                stage_b = {r["candidate_id"]: r for r in rows(source_file) if r["decision"] == POSITIVE}
                chapter = section["chapter"]
                line = section["section_start_line"]
                output = f"work/phase3-parallel/worker-{worker}/phase2_proposals/{chapter}/section-{line}.jsonl"
                records = rows(output)
                if set(stage_b) != {r["candidate_id"] for r in records}:
                    raise ValueError(f"Proposal ID set differs from frozen positive source: {output}")
                changed = False
                for proposal in records:
                    cid = proposal["candidate_id"]
                    reviewed = stage_b[cid]
                    identity = proposal.get("source_identity", proposal)
                    for key in ("source_revision", "source_file", "source_line", "original_source_statement_tex"):
                        if key in identity and identity[key] != reviewed.get(key):
                            raise ValueError(f"Source identity changed for {cid}: {key}")
                    for key in ("statement", "hypotheses", "conclusions", "logical_form"):
                        formulation = proposal.get("stage_b_reviewed_content") or proposal.get("reviewed_content") or proposal
                        if formulation.get(key) != reviewed.get(key):
                            raise ValueError(f"Reviewed content changed for {cid}: {key}")
                    if "source_statement_sha256" not in proposal:
                        continue
                    sha = hashlib.sha256(reviewed["original_source_statement_tex"].encode("utf8")).hexdigest()
                    if proposal["source_statement_sha256"] != sha:
                        proposal["source_statement_sha256"] = sha
                        fixes += 1
                        changed = True
                if changed:
                    (ROOT / output).write_text(
                        "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in records),
                        encoding="utf8",
                    )
                    files += 1
    print(json.dumps({"mechanical_sha256_corrections": fixes, "files_changed": files,
                      "source_text_or_theorem_content_modified": False}, sort_keys=True))


if __name__ == "__main__":
    main()

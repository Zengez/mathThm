#!/usr/bin/env python3
"""Build and audit frozen four-lane final Phase 2 source-equivalence queues.

Only metadata and queue construction: never approves a theorem or changes registries.
At setup: python scripts/phase2_final_parallel.py --generate
At setup or for worker: python scripts/phase2_final_parallel.py --check [--worker N]
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work/phase2-final-parallel"
PREVIOUS_BASE = "c57a162275ef35a7fe61e87f709627fd98ede4de"
INTEGRATED = "edb281cc48d7137c19e26a7db78ca39a0f0adf0f"
SOURCE_REV = "a04446e57ec1fbc252a871afcec7752fb2807b14"
POSITIVE = "source_equivalence_approved_pending_materialization"
CONTENT = ("statement", "hypotheses", "conclusions", "logical_form")
BRANCH = "work/phase2-final/parallel-base"
LANES = [f"work/phase2-final/chat-{n}" for n in range(1, 5)]
RECONCILED = "work/phase2-final/parallel-reconciled"
EXPECTED = {"plausible": 3061, "questionable": 701, "deferred": 104, "stage_b_held": 768}
MAX_SECTIONS_PER_BATCH = 11
MAX_CANDIDATES_PER_BATCH = 42


def git(*args):
    return subprocess.run(["git", *map(str, args)], cwd=ROOT, text=True,
                          capture_output=True, check=True).stdout.strip()


def rows(path):
    return [json.loads(s) for s in (ROOT / path).read_text(encoding="utf8").splitlines() if s.strip()]


def jwrite(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def failure(why):
    raise RuntimeError(why)


def frozen_inventory():
    """Use the completed Phase 3 pre-execution queues as exhaustive section inventory."""
    seen_sections, seen_ids = set(), set()
    sections, exclusions = [], {"nonplausible": [], "stage_b_held": []}
    outcomes = Counter()
    for old_worker in range(1, 5):
        path = f"work/phase3-parallel/worker-{old_worker}/PENDING.json"
        q = json.loads(git("show", f"{PREVIOUS_BASE}:{path}"))
        if q["source_revision"] != SOURCE_REV or not q["pending"]:
            failure(f"incorrect frozen Phase 3 input: {path}")
        for batch in q["pending"]:
            for section in batch["sections"]:
                src = section["file"]
                chapter, line, sha = section["chapter"], section["section_start_line"], section["blob_sha"]
                if src in seen_sections:
                    failure(f"repeated Stage B section: {src}")
                seen_sections.add(src)
                if git("hash-object", src) != sha:
                    failure(f"stage B blob mismatch: {src}")
                relative = f"{chapter}/section-{line}.jsonl"
                proof_path = f"work/phase3-parallel/worker-{old_worker}/proof_reviews/{relative}"
                proposal_path = f"work/phase3-parallel/worker-{old_worker}/phase2_proposals/{relative}"
                original = rows(src)
                positive = [r for r in original if r.get("decision") == POSITIVE]
                reviews = rows(proof_path)
                proposals = rows(proposal_path)
                pids = [r["candidate_id"] for r in positive]
                if pids != [r["candidate_id"] for r in reviews] or pids != [r["candidate_id"] for r in proposals]:
                    failure(f"Phase 3 input/outputs mismatch: {src}")
                if len(pids) != len(set(pids)):
                    failure(f"duplicate IDs in {src}")
                chosen = []
                for r in original:
                    cid = r["candidate_id"]
                    if cid in seen_ids:
                        failure(f"duplicate frozen candidate: {cid}")
                    seen_ids.add(cid)
                    if r.get("source_revision") != SOURCE_REV or r.get("source_file") != chapter + ".tex" or r.get("section_start_line") != line:
                        failure(f"incorrect source identity: {cid}")
                    if r.get("decision") != POSITIVE:
                        exclusions["stage_b_held"].append({
                            "candidate_id": cid, "stage_b_file": src, "stage_b_blob_sha": sha,
                            "reason": r.get("hold_reason") or r.get("review_note") or "Stage B held"
                        })
                for r, proof, proposal in zip(positive, reviews, proposals):
                    cid = r["candidate_id"]
                    if proof.get("source_revision") != SOURCE_REV or proof.get("phase2_authoritative_registered") is True or proof.get("published") is True:
                        failure(f"unusable provisional proof metadata: {cid}")
                    proof_hash = (proof.get("stage_b_reviewed_content_identity", {}).get("stage_b_blob_sha")
                                  or proof.get("stage_b_result_blob_sha") or proof.get("stage_b_blob_sha")
                                  or proof.get("stage_b_git_blob_sha"))
                    proposal_hash = (proposal.get("stage_b_result_blob_sha")
                                     or proposal.get("stage_b_blob_sha") or proposal.get("stage_b_git_blob_sha"))
                    if proof_hash is not None and proof_hash != sha:
                        failure(f"mismatched proof input hash: {cid}")
                    if proposal_hash is not None and proposal_hash != sha:
                        failure(f"mismatched proposal input hash: {cid}")
                    for key in CONTENT:
                        proof_content = proof.get("stage_b_reviewed_content") or {}
                        proposal_content = proposal.get("stage_b_reviewed_content") or proposal.get("reviewed_content") or {}
                        if key in proof_content and proof_content[key] != r.get(key):
                            failure(f"reviewed content differs in proof: {cid} / {key}")
                        if key in proposal_content and proposal_content[key] != r.get(key):
                            failure(f"reviewed content differs in proposal: {cid} / {key}")
                    if proposal.get("source_identity", {}).get("original_source_statement_tex") != r.get("original_source_statement_tex"):
                        failure(f"original source text differs: {cid}")
                    if r.get("decision") != POSITIVE or not r.get("review_note") or r.get("source_first_review") is not True:
                        failure(f"missing Stage B review: {cid}")
                    outcome = proof.get("outcome")
                    if outcome not in ("plausible", "questionable", "deferred"):
                        failure(f"unexpected provisional outcome {cid}: {outcome}")
                    outcomes[outcome] += 1
                    if outcome == "plausible":
                        chosen.append(cid)
                    else:
                        exclusions["nonplausible"].append({
                            "candidate_id": cid, "outcome": outcome,
                            "stage_b_file": src, "stage_b_blob_sha": sha,
                            "phase3_review_file": proof_path,
                            "reason": proof.get("reason", "")
                        })
                if chosen:
                    sections.append({
                        "chapter": chapter, "section_start_line": line,
                        "stage_b_file": src, "stage_b_blob_sha": sha,
                        "phase3_review_file": proof_path,
                        "phase3_review_blob_sha": git("hash-object", proof_path),
                        "phase2_proposal_file": proposal_path,
                        "phase2_proposal_blob_sha": git("hash-object", proposal_path),
                        "candidate_ids": chosen
                    })
    outcomes["stage_b_held"] = len(exclusions["stage_b_held"])
    if dict(outcomes) != EXPECTED:
        failure(f"population mismatch: {dict(outcomes)} versus {EXPECTED}; stop and investigate")
    if len(seen_ids) != 4634 or len(seen_sections) != 1244:
        failure(f"original inventory mismatch: IDs={len(seen_ids)}, sections={len(seen_sections)}")
    if len(set(x for s in sections for x in s["candidate_ids"])) != 3061:
        failure("plausible candidate ID collisions")
    return sections, exclusions, len(seen_sections)


def split_chapter(sections):
    """Chapter-local chunks, with complete sections. Greedy balance in candidate counts."""
    chapters = defaultdict(list)
    for s in sections:
        chapters[s["chapter"]].append(s)
    chunks = []
    for chapter, group in chapters.items():
        group.sort(key=lambda s: s["section_start_line"])
        # Large chapters can be assigned as consecutive section chunks to balance lanes.
        current, number = [], 0
        for s in group:
            count = len(s["candidate_ids"])
            if current and number + count > 310:
                chunks.append((chapter, current, number))
                current, number = [], 0
            current.append(s)
            number += count
        if current:
            chunks.append((chapter, current, number))
    lanes, counts = {n: [] for n in range(1, 5)}, {n: 0 for n in range(1, 5)}
    for chapter, group, count in sorted(chunks, key=lambda v: (-v[2], v[0], v[1][0]["section_start_line"])):
        n = min(counts, key=lambda worker: (counts[worker], worker))
        lanes[n].extend(group)
        counts[n] += count
    if max(counts.values()) - min(counts.values()) > 170:
        failure(f"unusually unbalanced workload: {counts}")
    return lanes, counts


def batching(sections, worker):
    batches, current, chapter, count = [], [], None, 0
    def flush():
        nonlocal current, chapter, count
        if current:
            batches.append({
                "batch_id": f"p2f-w{worker}-b{len(batches)+1:03d}",
                "chapter": chapter, "candidate_count": count,
                "sections": current, "status": "pending"
            })
        current, chapter, count = [], None, 0
    for s in sorted(sections, key=lambda x: (x["chapter"], x["section_start_line"])):
        size = len(s["candidate_ids"])
        if current and (s["chapter"] != chapter or len(current) >= MAX_SECTIONS_PER_BATCH or count + size > MAX_CANDIDATES_PER_BATCH):
            flush()
        chapter = s["chapter"]
        current.append(s)
        count += size
    flush()
    return batches


PROTOCOL = """# Authoritative Phase 2 — four-worker mathematical review protocol

## Exact scope and independence
Use ONLY the exact candidate IDs in your own worker-N/PENDING.json batches, derived from the audit-verified Stage B and Phase 3 artifacts. The provisional Phase 3 plausible screen selects the queue but is NOT evidence of Phase 2 mathematical equivalence. The Stacks original at the pinned commit is authoritative. Treat source facts in prior Stage A/B notes as aids, not an independent conclusion. Do NOT reread proofs or redo Phase 3 here.

For every candidate, inspect its pinned original Stacks theorem/lemma and the applicable standing assumptions, conventions, and definitions. Check that the proposed final statement is truly standalone, including all hypotheses, quantifier scopes, cases, equivalences, and conclusion parts. Detect changed strength, missing premises, ambiguous notation, and logical-form distortions. Verify the exact Stage B statement, hypotheses, conclusions and logical_form against the original, not merely a hash.

Record your actual reviewer identity or conversation identifier and the prior Stage A and Stage B reviewer identities from the proposal / Stage B row. This is an independent mathematical attempt; a new script/checksum does not establish independence. If reviewer independence cannot be supported, put the record on hold for adjudication.

## Start and checkpoint each complete batch
1. Work ONLY on branch work/phase2-final/chat-N. Verify its commit derives from work/phase2-final/parallel-base. Read this file, your PROMPT.md, your PENDING.json, and the first pending batch.
2. Check first batch's named Stage B, Phase 3 proof review and Phase 2 proposal files against their exact pinned Git blob SHAs. Use python scripts/phase2_final_parallel.py --check --worker N --first-batch for a fast targeted verification (and once initially a full --check --worker N is optional). Never scan whole corpus on every batch.
3. For each candidate_id, locate exactly its Stage B row and associated materialization proposal. Confirm original_source_statement_tex, source_file and line, pinned source revision, Stage A reconstruction, and the Stage B reviewer note. Read the original pinned Stacks source and relevant context. Do not infer mathematical approval from the provisional proof.
4. Write one substantive record per ID to work/phase2-final-parallel/worker-N/decisions/CHAPTER/section-L.jsonl, in the same order as the candidate_ids in that section. Each record has:
   - candidate_id; decision source_equivalence_approved OR source_equivalence_held
   - reviewer and source_first_review: true, proof_reviewed: false
   - prior_stage_a_reviewer and prior_stage_b_reviewer, source_revision, original source file/line, and referenced immutable input paths/SHAs
   - exact final_content fields (statement, hypotheses, conclusions, logical_form; also structured_cases and equivalence_sides if applicable) for approvals, with the approved_content_sha256 computed using scripts.phase2_authoritative.content_digest
   - a substantive semantic_review_note for approvals explaining source equivalence and context, OR a concrete hold_reason and correction/context/adjudication classification for holds.
5. Do not silently edit a Stage B formulation and approve it. For substantive corrections, hold the ID and describe proposed_correction separately. Such corrections need a fresh independent source-first review before central registration.
6. All candidates in a source section must receive a verdict before the section is complete. Record a batch checkpoint at worker-N/checkpoints/BATCH_ID.json with exact IDs and decision counts. Validate outputs and their order against the frozen batch. ONLY THEN remove the completed batch from your own PENDING.json (do not edit immutable ALLOCATION.json).
7. Commit and push your own worker folder changes to YOUR branch. Verify the pushed SHA, then move immediately to the next pending batch without waiting for another user prompt. A new conversation should resume from the first remaining batch using the committed queue/checkpoints. Commit in modest chapter-local batches.

## Strict isolation and authority
Do not edit other worker folders, shared ALLOCATION.json or EXCLUDED.json, authoritative registry, overlays, official Pass 3 files, published catalog, site, main, or the phase3 reconciled branch. Worker decisions are independently reviewed verdicts AWAITING CENTRAL REGISTRATION; do not set phase2_validated, phase3_eligible, pass3_plausible or published. Coordinator will reconcile overlaps/duplicates, source provenance and exact approved-content digests and then use the established Phase 2 authority machinery.

Report the completed and held IDs, section/batch counts, pending work, and the verified remote commit when the conversation ends. Never fake an approval or mark a partial section complete.
"""


README = """# Phase 2 final source-first mathematical approval — parallel worker infrastructure

This workspace was constructed from the complete audited Phase 3 integration branch. The audit verifies exactly 3,866 Stage B positive proposals with 3,061 provisional plausible, 701 questionable and 104 deferred Phase 3 screens, and 768 original Stage B holds. Only the 3,061 plausible IDs are active. The other 1,573 IDs are explicitly retained in EXCLUDED.json for later review.

The complete source sections, exact candidate IDs, stage B file blob SHAs, Phase 3 review file SHAs and materialization proposal blob SHAs are frozen in worker-N/PENDING.json. The four lanes are disjoint. ALLOCATION.json freezes counts and provenance; do not add discovered IDs. Workers may remove checked-off batches from their own pending queues after complete decision outputs and checkpoints are committed.

Authoritative registry and publication stay untouched; no worker has authority to register candidates. The original pinned Stacks revision is a04446e57ec1fbc252a871afcec7752fb2807b14.

Coordinator: run python scripts/phase2_final_parallel.py --check for the complete preflight BEFORE workers start; later audit worker checkpoint coverage against the frozen parallel-base commit. For quick worker verification use --check --worker N --first-batch. Use each worker-N/PROMPT.md to begin a separate independent conversation. The eventual central registration will need source-first approval evidence, exact approved-content digests, duplicate/adjudication review, and separate downstream Pass 3 admission and website testing.
"""


def generate():
    if not git("merge-base", "--is-ancestor", INTEGRATED, "HEAD") == "":
        failure("wrong base ancestor")
    sections, excluded, total_original_sections = frozen_inventory()
    lanes, counts = split_chapter(sections)
    allocations = []
    OUT.mkdir(parents=True, exist_ok=True)
    expected_union = set()
    for n in range(1, 5):
        batches = batching(lanes[n], n)
        worker_ids = [cid for b in batches for s in b["sections"] for cid in s["candidate_ids"]]
        if len(worker_ids) != len(set(worker_ids)) or expected_union.intersection(worker_ids):
            failure(f"duplicate IDs in worker {n}")
        expected_union.update(worker_ids)
        queue = {
            "schema": "maththm.phase2-final.worker-queue.v1",
            "worker": n, "branch": LANES[n-1],
            "source_revision": SOURCE_REV, "upstream_audit_commit": INTEGRATED,
            "frozen_previous_phase3_base": PREVIOUS_BASE,
            "selection_rule": "Exact IDs with provisional Phase 3 outcome plausible; all other outcomes and Stage B holds excluded",
            "expected_candidates": len(worker_ids), "initial_sections": len(lanes[n]),
            "initial_batches": len(batches), "pending": batches,
        }
        workdir = OUT / f"worker-{n}"
        jwrite(workdir / "PENDING.json", queue)
        prompt = f"""# Independent mathematical review — worker {n}

Repository Zengez/mathThm. Work ONLY on branch {LANES[n-1]} and ONLY in work/phase2-final-parallel/worker-{n}/.
Read work/phase2-final-parallel/WORKER_PROTOCOL.md, your PENDING.json, and the first pending batch. Your frozen assignment includes {len(worker_ids)} candidate IDs in {len(lanes[n])} complete sections and {len(batches)} batches. Inspect original pinned Stacks statements and context; independently assess the exact proposed Phase 2 formulations, not the proofs. Record substantive approve/hold evidence with prior reviewer identities. Do not modify authoritative registries or the site.

Immediately process the first pending batch, write exact source-first candidate decisions, validate complete-section checkpoint(s), update ONLY your queue, commit and push on {LANES[n-1]}, then automatically proceed to more batches. When stopping report verified remote SHA, complete sections, approvals, holds and remaining work. Do not merely describe the procedure.
"""
        (workdir / "PROMPT.md").write_text(prompt, encoding="utf8")
        for folder in ("decisions", "holds", "checkpoints"):
            (workdir / folder).mkdir(parents=True, exist_ok=True)
            (workdir / folder / ".gitkeep").write_text("", encoding="utf8")
        allocations.append({
            "worker": n, "branch": LANES[n-1],
            "queue": f"work/phase2-final-parallel/worker-{n}/PENDING.json",
            "candidate_count": len(worker_ids),
            "section_count": len(lanes[n]), "batch_count": len(batches)
        })
    if len(expected_union) != 3061:
        failure(f"expected 3061 distinct plausible IDs, got {len(expected_union)}")
    for x in excluded.values():
        x.sort(key=lambda item: item["candidate_id"])
    jwrite(OUT / "EXCLUDED.json", {
        "schema": "maththm.phase2-final.excluded.v1",
        "source_revision": SOURCE_REV,
        "nonplausible_count": len(excluded["nonplausible"]),
        "stage_b_held_count": len(excluded["stage_b_held"]),
        **excluded
    })
    jwrite(OUT / "ALLOCATION.json", {
        "schema": "maththm.phase2-final.parallel-allocation.v1",
        "source_revision": SOURCE_REV,
        "upstream_branch": "work/phase3/parallel-reconciled",
        "upstream_commit": INTEGRATED,
        "phase3_initial_queue_commit": PREVIOUS_BASE,
        "shared_base_branch": BRANCH,
        "reconciled_branch": RECONCILED,
        "initial_stage_b_positive_count": 3866,
        "initial_phase3_plausible_count": 3061,
        "excluded_questionable_count": 701,
        "excluded_deferred_count": 104,
        "excluded_stage_b_hold_count": 768,
        "original_section_count": total_original_sections,
        "active_section_count": len(sections),
        "total_active_batches": sum(x["batch_count"] for x in allocations),
        "authoritative_registry_updated": False,
        "published_catalog_updated": False,
        "workers": allocations
    })
    (OUT / "WORKER_PROTOCOL.md").write_text(PROTOCOL, encoding="utf8")
    (OUT / "README.md").write_text(README, encoding="utf8")
    print("GENERATED", json.dumps(allocations, sort_keys=True))
    check()


def check(worker=None, first_batch=False, verify_branches=False):
    a = json.loads((OUT / "ALLOCATION.json").read_text())
    exclusions = json.loads((OUT / "EXCLUDED.json").read_text())
    if a["source_revision"] != SOURCE_REV or len(a["workers"]) != 4:
        failure("invalid allocation header")
    if len(exclusions["nonplausible"]) != 805 or len(exclusions["stage_b_held"]) != 768:
        failure("exclusion population mismatch")
    exids = [x["candidate_id"] for name in ("nonplausible", "stage_b_held") for x in exclusions[name]]
    if len(exids) != len(set(exids)):
        failure("duplicate excluded candidate")
    seen_ids, seen_sections = set(), set()
    section_count = candidate_count = batch_count = 0
    for lane in a["workers"]:
        n = lane["worker"]
        if worker is not None and n != worker:
            continue
        queue = json.loads((OUT / f"worker-{n}/PENDING.json").read_text())
        if queue["worker"] != n or queue["branch"] != LANES[n-1] or queue["source_revision"] != SOURCE_REV:
            failure(f"incorrect worker queue header {n}")
        batches = queue["pending"][:1] if first_batch else queue["pending"]
        if not first_batch and len(batches) != lane["batch_count"]:
            failure(f"unexpected worker {n} batch count")
        for b in batches:
            if b["chapter"] != b["sections"][0]["chapter"]:
                failure("batch chapter mismatch")
            batch_count += 1
            for s in b["sections"]:
                section_count += 1
                src = s["stage_b_file"]
                if src in seen_sections or s["chapter"] != b["chapter"]:
                    failure(f"duplicate/bad section {src}")
                seen_sections.add(src)
                for pathfield, hashfield in (
                    ("stage_b_file", "stage_b_blob_sha"),
                    ("phase3_review_file", "phase3_review_blob_sha"),
                    ("phase2_proposal_file", "phase2_proposal_blob_sha")
                ):
                    if git("hash-object", s[pathfield]) != s[hashfield]:
                        failure(f"input hash mismatch: {s[pathfield]}")
                origin = rows(src)
                proof = rows(s["phase3_review_file"])
                orig_positives = [r for r in origin if r.get("decision") == POSITIVE]
                if [x["candidate_id"] for x in orig_positives] != [x["candidate_id"] for x in proof]:
                    failure(f"candidate order not preserved: {src}")
                selected = [r["candidate_id"] for r, p in zip(orig_positives, proof) if p["outcome"] == "plausible"]
                if selected != s["candidate_ids"]:
                    failure(f"section split or selected IDs mismatch: {src}")
                for cid in selected:
                    if cid in seen_ids or cid in exids:
                        failure(f"overlapping/held ID: {cid}")
                    seen_ids.add(cid)
                candidate_count += len(selected)
        if not first_batch and (sum(len(b["sections"]) for b in batches) != lane["section_count"]
                                or sum(b["candidate_count"] for b in batches) != lane["candidate_count"]):
            failure(f"worker counts inconsistent {n}")
    if worker is None and not first_batch:
        if candidate_count != 3061 or section_count != a["active_section_count"] or batch_count != a["total_active_batches"]:
            failure("global coverage count mismatch")
    if verify_branches:
        expected = git("rev-parse", "HEAD")
        for name in [BRANCH, *LANES, RECONCILED]:
            lines = git("ls-remote", "origin", f"refs/heads/{name}").splitlines()
            if len(lines) != 1 or lines[0].split()[0] != expected:
                failure(f"branch not pinned to common base: {name}")
    print("PASS", json.dumps({"worker": worker, "first_batch": first_batch,
                              "candidates": candidate_count, "sections": section_count,
                              "batches": batch_count, "verified_branches": verify_branches}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    action = ap.add_mutually_exclusive_group(required=True)
    action.add_argument("--generate", action="store_true")
    action.add_argument("--check", action="store_true")
    ap.add_argument("--worker", type=int, choices=(1, 2, 3, 4))
    ap.add_argument("--first-batch", action="store_true")
    ap.add_argument("--verify-branches", action="store_true")
    args = ap.parse_args()
    if args.generate:
        generate()
    else:
        check(args.worker, args.first_batch, args.verify_branches)

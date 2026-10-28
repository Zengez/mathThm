# mathThm harvesting — minimal three-pass runbook

**Status: October 28, 2026.** A lightweight, bounded Python toolkit exists. It is NOT a mathematical proof checker or autonomous research engine. No raw candidates or questionable cases are published automatically. See HARVEST_DESIGN.md and THEOREM_RECORD_CONTRACT.md.

## CURRENT CAMPAIGN OVERRIDE — prototype population and Pass 3

The initial Pass 2 bulk-discovery campaign is closed for the prototype. **Only the 9,683 candidate IDs in [harvest/active_candidate_ids.jsonl](harvest/active_candidate_ids.jsonl) are considered active.** The separate [active-pool manifest](harvest/ACTIVE_CANDIDATE_POOL.json) records the current recognized intake and batch membership. The historical Pass 1/2 files intentionally retain all original sources; they are NOT active-pool counts.

The deferred cases live exclusively for future discovery in [harvest/problem_candidates.jsonl](harvest/problem_candidates.jsonl) with difficulty groups and a [manifest](harvest/PROBLEM_CANDIDATES_MANIFEST.json). Pass 3 packets, manual Pass 3 decisions and staging ignore those IDs; routine status reports track only active intake. If a new separate research phase chooses to revisit these cases, start it deliberately and rebuild the pool only after accepted canonical decisions change.

For the existing three Stacks batches, the following commands now respect the allowlist:

```bash
python -m scripts.active_candidate_pool
python -m scripts.harvest_pipeline pass3-packets --workdir harvest/batches/stacks-bulk-2026-10-28 --source-root /path/to/pinned-stacks-source
python -m scripts.harvest_pipeline status --workdir harvest/batches/stacks-bulk-2026-10-28
```

Repeat Pass 3 for the other active Stacks batches. The pinned upstream source must be present for nontruncated proof excerpts. This transition does not read, screen, or publish any theorem proof.

---

## What each pass does

1. **Pass 1:** Scripts scan explicitly selected Stacks Project LaTeX chapter files for theorem/lemma/proposition/corollary environments followed by an apparent proof environment. They capture complete source statements, pinned source revision, source URL, exact source line, proof location and source confidence. They **do not read or assess the proof**. Pass 1 false positives are acceptable.
2. **Pass 2:** A statement-structuring packet is created from each raw candidate. Up to two local same-file referenced theorem statements may be supplied as context, without chasing further dependencies. A human or model reviewer adds the faithful displayed restatement, hypotheses, conclusions and initial tags. Unresolved context becomes needs_context.
3. **Pass 3:** A bounded proof excerpt is prepared from the original source; a human/model reviewer scans it and submits a verdict. Plausible means a full quick scan saw no obvious issue; questionable means a strict stop was reached; rejected requires an identifiable issue. Truncated packets cannot become plausible without an explicit assertion that a complete scan was actually done elsewhere. **The scripts never assign a mathematical verdict.**

Questionable, rejected and needs_context items remain in a separate needs_more_investigation.jsonl file with their source/proof URLs. Rejection of a cited proof does NOT assert that the theorem itself is false. Source confidence and proof-screening confidence stay distinct.

## Files and tools

- scripts/harvest_stacks.py — bounded, source-native Pass 1 extraction; pinned revisions; idempotent candidate IDs.
- scripts/harvest_pipeline.py — Pass 2/3 review packets and decisions, investigation queue, restart checkpoint, explicit staged promotion.
- .github/workflows/harvest-stacks.yml — manual GitHub Action for ONE selected Stacks chapter (limit 1–500), producing downloadable raw candidate artifacts only.
- tests/test_harvest_pipeline.py — offline end-to-end tests.
- data/theorems.json — current published catalog, never modified by Pass 1/2/3.
- .harvest_runs — recommended local workspace, not part of the public site.

## Option A: Start a Pass 1 in GitHub

Visit https://github.com/Zengez/mathThm/actions/workflows/harvest-stacks.yml and select Run workflow. The default chapter is categories.tex, default maximum is 100. The workflow fetches a pinned snapshot of that single public Stacks source chapter, runs mechanical Pass 1, and uploads a stacks-raw-candidates artifact containing pass1.jsonl and checkpoint.json. Download/unpack that artifact into a local workspace to continue. It does **not** push to the repo or publish a theorem. Its source strategy does not depend on Stacks's less-stable public API.

## Option B: Start Pass 1 locally

Clone/check out the Stacks Project at a known full 40-hex-digit commit SHA. Replace SOURCE_COMMIT below with that actual SHA:

    python scripts/harvest_stacks.py --source-root /local/stacks-project --source-ref SOURCE_COMMIT --files /local/stacks-project/categories.tex --batch-id stacks-categories-001 --max-candidates-per-file 100 --output-dir .harvest_runs/stacks-categories-001

For source fidelity, the raw candidate file stores full original LaTeX statement text, not a source-derived paraphrase. The accepted website uses separately reviewed faithful statements and preserves attribution. Stacks material is under the GNU Free Documentation License; review reuse requirements before publicly reproducing substantial original language.

## Pass 2 commands

    python scripts/harvest_pipeline.py pass2-packets --workdir .harvest_runs/stacks-categories-001 --source-root /local/stacks-project

This writes pass2_packets.jsonl. A reviewer/model creates a JSONL file where each line is one object of this shape:

    {"candidate_id":"candidate.stacks.REPLACE_WITH_ACTUAL_ID","context_status":"resolved","statement":"If $f$ is continuous on a compact space $X$, its image is compact.","hypotheses":["$X$ is compact","$f$ is continuous"],"conclusions":["The image of $f$ is compact"],"hypothesis_tags":["compactness","continuity"],"conclusion_tags":["compactness"],"area":"Topology","title":"Compact image","context_note":""}

This is an EXAMPLE, not an extraction from a specific source. For unresolved local assumptions, set context_status to needs_context and supply a nonempty context_note rather than inventing hypotheses/conclusions.

    python scripts/harvest_pipeline.py pass2-apply --workdir .harvest_runs/stacks-categories-001 --decisions pass2-decisions.jsonl

## Pass 3 commands

    python scripts/harvest_pipeline.py pass3-packets --workdir .harvest_runs/stacks-categories-001 --source-root /local/stacks-project --max-proof-chars 7500

This writes pass3_packets.jsonl for resolved candidates only. A human/model reads the provided proof or visits its cited URL, without substantial extra research. Reviewer decision example:

    {"candidate_id":"candidate.stacks.REPLACE_WITH_ACTUAL_ID","outcome":"questionable","scan_completed":false,"reason":"Proof references another argument whose validity would require substantial background; stop rule reached","proof_checked_on":"2026-10-28"}

For plausible, require scan_completed=true. For rejected, require a positive identifiable issue in reason. A proof excerpt marked truncated cannot be promoted as plausible unless a reviewer actually scans the full proof at its source and explicitly states full_proof_reviewed_externally=true. If no ending proof marker was found, manually_verified_proof_completion=true requires actual evidence that the proof appears finished, not guesswork.

    python scripts/harvest_pipeline.py pass3-apply --workdir .harvest_runs/stacks-categories-001 --decisions pass3-decisions.jsonl

## Investigation queue and staging

    python scripts/harvest_pipeline.py status --workdir .harvest_runs/stacks-categories-001

The checkpoint is regenerated from the actual stage files; decisions and raw candidates persist independently. needs_more_investigation.jsonl holds all questionable/rejected and context-blocked entries with reasons and provenance. No mathematical validity implication is made by a Pass 3 verdict.

Only fully structured, explicitly plausible candidates can enter a staged catalog:

    python scripts/harvest_pipeline.py promote --workdir .harvest_runs/stacks-categories-001 --catalog data/theorems.json --output .harvest_runs/stacks-categories-001/staged-theorems.json

This validates the accepted schema. It does **not** modify data/theorems.json, git, GitHub Pages or mathDef. A later explicit review and commit of a staged catalog is required for public publication. Rerunning steps is idempotent, and conflicting decisions require explicit --replace rather than overwriting evidence silently.

## Resource limits and next phase

Keep the first run source-driven and simple: one or a few files, bounded 25–100 candidate batches, no dependency graph, no recursive math research, no multiple-proof classification, no semantic duplicate reconciliation. The initial target remains at least 200–300 provisionally accepted theorems before reevaluating website search/performance design. The tools support human or model reviewers, but don't themselves run an LLM or claim to verify logic.

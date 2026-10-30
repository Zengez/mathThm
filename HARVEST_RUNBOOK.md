# mathThm harvest and Stage A runbook — current workflow

This document describes the **active** workflow. The previous experimental
Pass 1/Pass 2/section-walk pilot instructions are preserved in Git history,
not run as a stack of extra scripts or GitHub Actions. See `AGENTS.md` for
the efficiency-first development policy.

## Canonical population and immutable evidence

- The pinned Stacks source revision is `a04446e57ec1fbc252a871afcec7752fb2807b14`.
- The canonical active intake has **9,675** distinct IDs in
  `harvest/active_candidate_ids.jsonl`. Historical raw Pass 1 and Pass 2
  records in `harvest/batches/` remain the original source evidence.
- The deferred false-positive/complex research intake remains separate at
  `harvest/problem_candidates.jsonl`; it is not part of routine Stage A.
- Mathematical approval evidence lives on the independent
  `codex/phase2-validation` branch in
  `harvest/PHASE2_AUTHORITATIVE_REGISTRY.json` and its referenced overlays.
  Do not alter source-review history to manipulate current workload.
- The public `data/theorems.json` is not changed by preparation or reviews.

## Stage A: one pending queue, source order, no per-item status lookups

The working branch is `feature/phase2-chapter-preparation`.
Its prepared inputs live at
`harvest/phase2_prepared/a04446e57ec1/`:

```text
INDEX.json
<chapter>/MANIFEST.json
<chapter>/SECTIONS.jsonl
<chapter>/CANDIDATES.jsonl
```

The **existing CANDIDATES.jsonl files contain only unfinished Stage A
candidates**. The five chapters already reviewed by Codex have had **655
approved candidates removed in place**, leaving **9,020** pending inputs
across 115 chapters. Holds/unapproved candidates stay pending. No
`STAGE_A_PENDING_*`, `CODEX_REVIEWED_*`, skip tables or supplementary
per-candidate lookups are part of this runtime pathway.

A Stage A batch reads consecutive **complete** `SECTIONS.jsonl` records
once in physical source order, with intervening zero-candidate sections
included, and consumes only that section's pending candidate records.
All source context remains proof-free. Maintain scope chronologically:
standing assumptions apply only within their actual scope; temporary
lemma/proposition hypotheses expire at the environment end. Definitions
supply mathematical meaning rather than automatic hypotheses. Expand
source references where needed and mark unresolved logical/context issues
as holds without inventing assumptions.

Stage A produces independent standalone theorem *drafts*, not mathematical
source-equivalence approvals. Codex independently checks quantifiers,
existential witnesses, alternative sufficient hypotheses, equivalences,
scope, and conclusions. The approved content must be materialized through
the established Phase 2 authoritative process before Phase 3 eligibility.

## On completion of a Codex review batch (one-time maintenance)

At the **batch boundary**, reconcile newly approved candidate IDs with
the existing authoritative reviews. Then directly edit the *same* chapter
`CANDIDATES.jsonl` files: remove newly approved records. Remove those IDs
from the corresponding section `candidate_ids` arrays, and update the
chapter `MANIFEST.json` counts and SHA-256 digests and `INDEX.json`
counts. Do this once for the committed batch. Do not repeat this resolution
while reviewing each section or create another pending-file layer.
Git retains the previous packets and the authoritative Codex branch retains
the approved formulations.

## Preparation code and checks

The single chapter-preparation entrypoint is
`scripts/phase2_prepare_chapters.py`. It is needed only when generating
**previously unprepared** pinned-source chapters. Existing prepared packets
are not rebuilt each Stage A run. The exact source commit must match.

```bash
python -m unittest discover -s tests -q
python -m scripts.phase2_verify_prepared --source-root upstream/stacks
# Only if new chapters genuinely need input generation:
python -m scripts.phase2_prepare_chapters --chapters all --only-missing
```

The `phase2-prepare-chapters.yml` Action runs generation in a single batch,
verifies once, and commits once, instead of executing a full repository
verification for each chapter. `phase2-review-integrity.yml` is read-only.
`pages.yml` publishes the existing reviewed website independently.
The generic harvesting and duplicate/Phase 3 precheck Actions remain
available if those later phases actually require them.

## Safety and efficiency constraints

- Do not automatically promote preliminary Pass 2 splits or Stage A drafts.
- Do not read theorem proofs during Stage A or infer source equivalence from
  mechanical hashes, style tests or a status flag.
- An unapproved hold is not a completed mathematical review.
- Avoid repeated parsing, extra queue/state files, per-candidate status
  tables, redundant full-corpus scans and obsolete batch-size entrypoints.
  Prefer one well-scoped pass with boundary checks and actual benchmarks.
- Preserve historical mathematical evidence and useful logical-scope
  regression tests. Consult Git history or `WORK_CHECKPOINT.md` for
  earlier pilot commands; they are not an alternative active workflow.

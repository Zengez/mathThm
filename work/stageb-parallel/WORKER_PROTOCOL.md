# Four-worker Stage B: shared operating protocol

This run uses a frozen combined Stage A + Stage B tree. The immutable assignment is `work/stageb-parallel/ALLOCATION.json`. Worker `N` owns **only** `work/stageb-parallel/worker-N/**` on branch `work/stageb/chat-N`. Do not modify the other three queues, source Stage A reconstructions, existing Stage B outputs, `harvest/PHASE2_AUTHORITATIVE_REGISTRY.json`, or shared scripts. Do not rebase or merge another worker branch while processing.

## What is allocated

Each source chapter belongs to exactly one worker, including ALL of its Stage A reconstruction files. This avoids cross-worker collisions even when an old chapter contains overlapping preparation passes. Inside the chapter, process sections consecutively in the source order, **never split an individual section**. Zero-candidate/context-only sections can be traversed as context but need no review outcomes.

The initial `PENDING.json` contains chapter tasks and file pointers, **not a certification that every row is ready**. A one-time chapter-local preflight must derive exact candidate IDs before review:

1. Read the chapter's `stage_a_reconstructions` from `PENDING.json` and their Stage A manifests/context/checkpoints. Do not scan every other chapter.
2. Accept only canonical candidate IDs having `decision == "reconstruction_completed_awaiting_independent_stage_b_validation"`, an empty `stage_a_remaining_work`, the pinned source revision, valid source locators, and no completed independent validation. Reject malformed or unresolved records.
3. Exclude every candidate already recorded in any path in `harvest/PHASE2_AUTHORITATIVE_REGISTRY.json`; also exclude all IDs from the prior Codex Stage B `SELECTION.json` files (which contain reviewed approvals **and** holds), and Stage A further-work lists including `modules`. Previously held cases are for the final sweep, not this first pass.
4. Deduplicate exact IDs across overlapping Stage A source files. If two versions materially disagree, **hold that ID for later reconciliation**, not silently pick one. Record its alternate provenance. Do not regenerate prior approvals.
5. Partition remaining IDs into sections using explicit section ordinals or source-line intervals in the corresponding MANIFEST; do not infer section numbers from unrelated chapters. If source-section mapping cannot be verified, defer the candidate to the final sweep.
6. Work through manageable sets of **consecutive full sections**, roughly 40–75 ready IDs when possible. A large section is processed intact, or resumed at safe candidate checkpoints within that same section with no incomplete-section approval.

## Review rules

Stage A is **not** mathematical approval. Independently check the pinned original source theorem statement against the proposed standalone `statement`, `hypotheses`, `conclusions`, logical form, scopes, quantifiers, diagrams, named contexts and source-specific definitions. Preserve exact source equivalence; no strengthening/weakening. Use the source-ordered context ledgers as evidence, not as automatic assumptions. Only the original formal statement and source-safe excerpts may be shown to the Stage B reviewer.

**Proof exclusion is mandatory.** Never read raw, unmasked Stacks source slices or any proof, informal argument, remark, or Situation exposition. When further source context is needed, use `scripts/phase2_safe_source.py` on the pinned source. If safe evidence is unavailable, record a hold; do not bypass the viewer. The prior `flat.tex` and `dualizing.tex` proof-exposure incidents are not review material.

For a candidate whose Stage A draft is already correct, a separate Stage B worker can independently record an approval, with its own reviewer ID, exact source ID, provenance, and source-first reasons. If a substantive repair is required, create the corrected draft as a **proposal requiring a distinct later independent review** rather than self-approving your own correction. Difficult cases should be held promptly. Never assert `phase2_validated`, `phase3_eligible`, or publication in these worker-only records.

## Exclusive results and commits

Write immutable per-section files under `work/stageb-parallel/worker-N/results/<chapter>/section-XXXX.jsonl`. One JSON object per assigned ready ID handled, with at least:
`candidate_id`, `source_file`, `source_line`, `section_ordinal`, `stage_a_artifact`, `decision` (one of `source_equivalence_approved_pending_materialization`, `held_for_correction_or_context`), `reviewer`, `source_first_review`, `proof_reviewed` (false), `review_note`, and, for approvals, `statement`, `hypotheses`, `conclusions`, `logical_form`. Preserve the original source and a proposed correction as separate fields, never overwrite it.

After finishing one or more **complete** source sections, validate that every ready ID in those sections has exactly one result, commit the result files, and advance only your chapter task's `next_section_ordinal` in your OWN `PENDING.json` in the SAME commit. For a completed chapter, remove its entry from `pending` entirely. Do not delete or alter `ALLOCATION.json` (the permanent audit ledger). On interruption, resume from your queue cursor and existing committed section outputs; never silently redo completed IDs. Commit after each bounded group of complete sections. Do not begin a new chapter if a previous chapter has incomplete work.

At the end of each reply report: chapters fully completed, ready IDs reviewed, approvals pending materialization, holds, remaining chapter tasks, and last pushed commit SHA. Do not claim a push succeeded without verifying it.

## Integration and final sweep

Merge worker branches into a **separate integration branch**, not into each other; changes should be confined to disjoint worker directories. The coordinator must verify union and uniqueness of candidate IDs; check each section against its prepared eligible IDs; verify corrected proposals received an independent second review; and use existing `scripts/phase2_review_workflow.py` / `scripts/phase2_authoritative.py` to materialize individually validated approvals **only after** their schema and provenance requirements are met. Do not directly append these preliminary result records to the authoritative registry.

The final sweep compares the canonical active candidate pool with all historical approvals, reviewed/held IDs, and four result sets. It detects missed or unmapped Stage A candidates, duplicate preparation records, uncompleted chapter ranges, prior Codex holds, and Stage A holds. No candidate can become Phase 3 eligible through counting alone.

**Efficiency:** load at most one chapter and its relevant checkpoint/context at a time. Avoid repository-wide scans, repeated prerequisite discovery, or elaborate skip tables during candidate review. The immutable allocation serves as the only global assignment registry.

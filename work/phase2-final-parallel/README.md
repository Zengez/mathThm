# Phase 2 final source-first mathematical approval — parallel worker infrastructure

This workspace was constructed from the complete audited Phase 3 integration branch. The audit verifies exactly 3,866 Stage B positive proposals with 3,061 provisional plausible, 701 questionable and 104 deferred Phase 3 screens, and 768 original Stage B holds. Only the 3,061 plausible IDs are active. The other 1,573 IDs are explicitly retained in EXCLUDED.json for later review.

The complete source sections, exact candidate IDs, stage B file blob SHAs, Phase 3 review file SHAs and materialization proposal blob SHAs are frozen in worker-N/PENDING.json. The four lanes are disjoint. ALLOCATION.json freezes counts and provenance; do not add discovered IDs. Workers may remove checked-off batches from their own pending queues after complete decision outputs and checkpoints are committed.

Authoritative registry and publication stay untouched; no worker has authority to register candidates. The original pinned Stacks revision is a04446e57ec1fbc252a871afcec7752fb2807b14.

Coordinator: run python scripts/phase2_final_parallel.py --check for the complete preflight BEFORE workers start; later audit worker checkpoint coverage against the frozen parallel-base commit. For quick worker verification use --check --worker N --first-batch. Use each worker-N/PROMPT.md to begin a separate independent conversation. The eventual central registration will need source-first approval evidence, exact approved-content digests, duplicate/adjudication review, and separate downstream Pass 3 admission and website testing.

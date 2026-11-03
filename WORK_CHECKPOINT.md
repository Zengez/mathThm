# Current mathThm checkpoint — 2026-11-03

Production is running from `main` with the Phase 2 canonical master and search UI. The 4,132-record source of truth is `data/maththm_master.jsonl`: 3,943 approved, 189 held. Publication is deterministic via `scripts/publish_phase2_catalog.py --all`; it must not trigger a new broad review.

**Unfinished material protected for later:** the 189 held canonical records (and corresponding `work/phase2-final-publication/BLOCKERS.json`) plus the 1,304 deferred Stacks Project candidates in `harvest/problem_candidates.jsonl`. Source records, contextual evidence and rationale remain in `harvest/`. Do not discard or auto-promote them.

**Active maintenance:** Pages build/deploy and UI regression; on-demand small Stacks harvest; separate scheduled Wikipedia dump URL crawl on dedicated branches. The older batch-specific Phase 2 review/section-walk jobs, temporary shards and worker prompts are finished and have been removed from `main`.

Read `README.md` for ordinary tasks and `harvest/PROBLEM_CANDIDATES_README.md` for the detailed deferred inventory. Historical execution checkpoints can be inspected in Git history rather than maintained as current instructions.

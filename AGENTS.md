# mathThm agent instructions — efficiency-first

For this repository, optimize for the fastest correct *overall execution pathway*, not the smallest immediate code change.

1. Rewrite and consolidate existing code/data when requirements change. Do not accumulate adapter scripts, compatibility wrappers, auxiliary ledgers, redundant flag sets or lookups.
2. Read source/context once per consecutive complete section; accumulate and correctly expire local hypotheses, maintain source provenance, and use one pass when possible. Batch file I/O and precompute shared inputs once per batch.
3. When a candidate's independent mathematical source-equivalence review is **approved**, remove it from the existing Stage A prepared candidate inputs on the preparation branch **once at handoff** (plus companion section IDs, manifest hashes and index). Do not impose an approval-status lookup on every subsequent Stage A operation. Holds/unapproved cases remain pending.
4. Preserve the authoritative Phase 2 review registry, original pinned Stacks source evidence, candidate IDs, mathematical approval gates and context regression tests. Stage A drafts are not approvals and proofs are not screened in Stage A.
5. Before deleting obsolete machinery, check active imports, Actions callers, tests and output dependencies; Git history supplies old versions. Eliminate unused paths and duplicated state rather than keeping both old and new pipelines.
6. Benchmark or quantify actual repeated work and execution cost. Put integrity validation at run/handoff boundaries, not in each section/candidate iteration.

Current pending Stage A packet branch: `feature/phase2-chapter-preparation`. Its canonical queue is `harvest/phase2_prepared/a04446e57ec1/<chapter>/CANDIDATES.jsonl`, after completed approvals were removed directly; do not regenerate `STAGE_A_PENDING_*` or `CODEX_REVIEWED_*` sidecar files.

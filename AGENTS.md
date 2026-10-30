# mathThm agent instructions

## Efficiency-first development and Stage A (ChatGPT and Codex)

- Optimize the resulting design for execution cost, source reads, and clarity—not the smallest code diff. Edit/rewrite active logic, remove obsolete implementations, and do not pile on wrappers, compatibility paths, flags, or repeated per-candidate lookups.
- The canonical Stage A queue is `harvest/phase2_prepared/a04446e57ec1/<chapter>/CANDIDATES.jsonl`, containing only unfinished candidates. `SECTIONS.jsonl` retains *all* consecutive physical source sections for contextual reconstruction and its `candidate_ids` lists unfinished members only.
- After Codex completes a batch, once at the handoff boundary remove approved records from the existing chapter candidates and section IDs, update the chapter manifest counts/SHA-256 digests and INDEX. Do not add separate pending/status tables, parallel queue files, or completion checks in every Stage A candidate operation. **Retain holds/unapproved cases.**
- Stage A processes consecutive **complete** sections in source order and maintains positive and negative mathematical scope (temporary hypotheses expire). Definitions and standing conventions are not automatically theorem hypotheses. Proof material must stay excluded.
- Prefer a single source/context traversal of the selected sections; precompute necessary context once, batch file I/O, and validate at input/output boundaries rather than re-scanning the full corpus for every item. Measure actual work/benchmarks before claiming improved performance.
- Before deletion check active imports/callers, tests, artifacts and GitHub Actions dependencies. Keep source evidence and authoritative mathematical reviews; old implementation history is available through Git.
- Never automatically promote a mechanical or editorial Stage A draft to mathematical source-equivalence approval, Phase 3 proof-screening, or publication.

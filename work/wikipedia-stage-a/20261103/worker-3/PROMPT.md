# mathThm Wikipedia Stage A — editorial worker 3 (exclusive lane)

Repository: `Zengez/mathThm`  
Prepared source branch: `work/wikipedia-stage-a-20261103`  
Your exclusive output branch: `work/wikipedia-stage-a/worker-3`

**Start processing immediately; this is statement preparation, not a new theorem-discovery, duplicate-detection, or proof-validation project.**

## Your exact 280-URL assignment

- Main queue (273 rows): `work/wikipedia-stage-a/20261103/worker-3/needs_interpretation.jsonl`
- Small tentative-split queue (7 rows): `work/wikipedia-stage-a/20261103/worker-3/mechanical_suggestions.jsonl`

Both files belong exclusively to worker 3. **Process both; the machine suggestions are not approved theorem formulations.** All four workers' URL sets are disjoint. Do not inspect or modify the other workers' queues.

For each row, use the already-fetched `source_excerpt`, `source_statement_excerpt`, `source_section`, and original Wikipedia URL to identify the *central mathematical result*. Prepare a faithful, stand-alone `statement`, and separate `hypotheses` and `conclusions` in the same style as the published mathThm records. Preserve quantifiers, ambient definitions, scope, and directionality. A theorem with an `if and only if` must retain both directions; do not silently drop one.

The Wikipedia text extractor preserved displayed math and list items, but a selected paragraph can still refer to a following formula or a missing definition. Check adjacent excerpt paragraphs; open the article briefly only if necessary. If source material is insufficient or multiple fundamentally different theorems are inseparable, mark the candidate `held_for_source_clarity` and move on. Prioritize throughput over unraveling ambiguities; never guess missing assumptions.

## Deliverable

On your exclusive output branch, save or incrementally update:
`work/wikipedia-stage-a/20261103/worker-3/editorial_decisions.jsonl`

Each JSONL record must include:
- `candidate_id`, `url`, `title`, and `source_statement_excerpt` from the input
- `statement` (faithful unified claim, or null if held)
- `hypotheses` and `conclusions` (arrays; preserve mathematical logic)
- `status`: `standalone_prepared` or `held_for_source_clarity`
- A short `editorial_note` describing any uncertainty or the hold reason
- Optional `source_section`, `equivalence_sides`, and `structured_cases` when genuinely needed

Do not add any of this to `data/theorems.json` or `data/maththm_master.jsonl`. Do not validate proofs, do a fresh global duplicate search, invent missing lemmas, or audit the source mathematics. This is only Wikipedia Stage A statement preparation.

Work in batches of about 25–50 candidates, **commit progress regularly**, and resume by stable `candidate_id`. You may allow a few candidates to remain held; do not spend disproportionate time resolving them. At completion, account for all 280 assigned IDs exactly once (including the 7 tentative-split entries).

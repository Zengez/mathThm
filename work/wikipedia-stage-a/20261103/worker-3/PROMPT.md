# Wikipedia Stage A — worker 3 (exclusive lane)

Repository: Zengez/mathThm
Base branch: work/wikipedia-stage-a-20261103
Input: work/wikipedia-stage-a/20261103/worker-3/needs_interpretation.jsonl

Review your entire *assigned* queue (currently 273 rows). Only split the
Wikipedia top excerpt into an accurate theorem statement, separate hypotheses
and conclusions, and preserve quantified conditions and scope.
Use `source_excerpt`, `source_statement_excerpt`, `source_section`, and the
live Wikipedia article when genuinely necessary. An article may contain multiple
statements; extract one distinct central result first and flag others explicitly.
**Do not** invent conditions, assume a theorem from the page title, collapse
two-direction equivalences, check proof correctness, or perform another
duplicate search. A difficult/unclear case may be held, not guessed.

Write your own results to `work/wikipedia-stage-a/20261103/worker-3/
editorial_decisions.jsonl` on your own branch
`work/wikipedia-stage-a/worker-3`, without editing other workers'
files. Each decision must retain `candidate_id`, `url`, `source_statement_excerpt`,
`statement` (or null), `hypotheses`, `conclusions`, and status
(`standalone_prepared` or `held_for_source_clarity`) with a concise reason.
Work in batches; save results incrementally, resuming by candidate ID only.

The 7 mechanically split cases for this lane are separate in
`mechanical_suggestions.jsonl`. These are **draft suggestions, not verified
mathematical formulations**. Do not promote them automatically to the public
catalog. This work is statement preparation only, not a proof review.

# Publication worker 3 — publish approved canonical records

**Exclusive GitHub branch:** `work/phase2-publication/chat-3`
**Coordinator baseline branch:** `work/phase2-final-publication`
**Assignment:** IDs `candidate.stacks.<hex>...` with first hex digit **8–b**.
**Expected records:** 1057 = 1005 approved + 52 held.
**Only allowed output files:** `work/phase2-final-publication/shards/worker-3.json` and `work/phase2-final-publication/workers/worker-3/RESULT.json`.

Inspect live branch heads and the current coordinator branch before starting; do not assume an old SHA is latest. Read `work/phase2-final-publication/README.md`, `scripts/publish_phase2_catalog.py`, and this prompt.

Execute `python scripts/publish_phase2_catalog.py --worker 3` on **your exclusive branch**. This reads the permanent materialized `data/maththm_master.jsonl` directly and transforms your assigned approved canonical records into full publishable v1-revision-2 theorem objects, while accounting for held records and any concrete technical blockers. Do **not** reconstruct the old worker reviews or re-review already approved mathematics.

Inspect the generated worker-3.json's exact coverage and statuses. Accept source-equivalence approvals. Keep the original approved statements/hypotheses/conclusions untouched, sources/proof references and reviewer provenance intact. For an approved record whose proof screening was not independently recorded, preserve the pinned source reference with `source_reference_only`; never fabricate an inspected-proof status. Empty hypotheses are allowed for unconditional results; flat equivalence-side strings are transformed into singleton search groups. Do not create semantic theorem mergers on similarity alone.

If there is a concrete, local technical error (broken URL, malformed output, missing essential field), either make a purely mechanical, evidence-backed correction within **your own shard output** or mark that specific ID `blocked` with exact reason. Do not change canonical master, common scripts, website catalog, other shards, or any other worker's files. Do not add broad new review gates.

Write `RESULT.json` with exact counts: assigned IDs, approved transformed, held, blocked, screened proof links versus source-only links, mechanically consolidated duplicate IDs if any, and explicit outstanding blockers. Commit both your complete shard and your result to `work/phase2-publication/chat-3`; return commit SHA and files to the coordinator. The coordinator owns cross-shard consolidation, final site validation and deployment.

If the coordinator's single-pass action has **already generated all four shards and published them successfully**, do not redo the transformation or overwrite newer data. In that case, report that your lane was automatically published and limit attention to any specifically reported blockers in your ID range.

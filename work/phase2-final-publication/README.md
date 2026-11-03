# Final publication — execution coordinator

Canonical input: `data/maththm_master.jsonl` from the mechanically reconciled master, never rebuilt from the historical review files. Approved Phase 2 decisions are authoritative for source-equivalence. The website dataset is derived, not a competing source of mathematical truth.

## Exact disjoint assignments

| Worker | Canonical ID first hex digit | Master records | Approved | Held | Exclusive output |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | 0–3 | 1,000 | 959 | 41 | `shards/worker-1.json` |
| 2 | 4–7 | 1,033 | 984 | 49 | `shards/worker-2.json` |
| 3 | 8–b | 1,057 | 1,005 | 52 | `shards/worker-3.json` |
| 4 | c–f | 1,042 | 995 | 47 | `shards/worker-4.json` |

The partition uses the first hexadecimal digit *after* `candidate.stacks.`, not the alphabetical chapter name or a mutable row number.

## Execution

```bash
python scripts/publish_phase2_catalog.py --worker 1     # replace 1 by lane number
python scripts/publish_phase2_catalog.py --all          # faster coordinator single-pass generation
python scripts/publish_phase2_catalog.py --integrate    # integrate checked worker outputs
python -m scripts.theorem_schema data/theorems.json
python -m unittest discover -s tests -v
node --test tests/test_search.cjs tests/test_ui_smoke.cjs tests/test_mathdef_v2.cjs tests/test_definition_links.cjs
```

`--all` generates every shard plus the integrated catalog in one pass. It is preferred if the automatic conversion succeeds: do **not** artificially force four chat workers to repeat deterministic processing. The workers are available for independent technical exceptions or if the single-pass workflow needs recovery. Their outputs are collision-free, and a worker can commit its complete derived shard directly.

Website record shape is the existing `maththm.theorems.v1` contract revision 2, with additional `canonical_ids`, `canonical_sources`, and `phase2_approval` provenance. The canonical master is not edited. The 20 existing prototype results are frozen in `prototype_baseline.json` and preserved on integration. Duplicate merger requires identical normalized full statement, hypotheses, conclusions, logical form, equivalence sides and structured cases; uncertainty remains separate.

Only concrete missing fields, genuinely invalid references, or unrepresentable schema data block one record. An empty hypotheses list can be mathematically accurate and is allowed for previously approved formulations. Early historically approved records without a separate Phase 3 proof-screening record receive a pinned **source reference only**, not a falsely asserted proof audit. The visible UI marks the distinction. All proof and source URLs, individual candidate IDs and reviewer attribution remain traceable.

Coordinator owns `scripts/publish_phase2_catalog.py`, validator/UI common changes, combined `data/theorems.json`, and GitHub Pages deployment. Workers must not modify these shared files. Worker assignments: see `workers/worker-N/PROMPT.md`. The automatic GitHub Actions job may complete all shards faster than four chat sessions; if so, do not duplicate its work.

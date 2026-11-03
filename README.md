# mathThm — searchable mathematical theorems

**Production site:** https://zengez.github.io/mathThm/  
**Status (2026-11-03):** Production reads the permanent reviewed Stacks master (`data/maththm_master.jsonl`) and publishes eligible, already-approved records using `scripts/publish_phase2_catalog.py`. This is a publication step, **not** another mathematical review. The existing 20-prototype baseline is retained.

## Permanent data and deferred work

- `data/maththm_master.jsonl` — authoritative 4,132 Phase 2 decisions: **3,943 approved, 189 held**. Hold reasons and source references are protected. Never reconstruct the master from removed worker queues.
- `data/theorems.json` — generated public catalog, including source attribution and proof-screening distinctions. It is not an alternate source of truth.
- `harvest/problem_candidates.jsonl` + `harvest/PROBLEM_CANDIDATES_README.md` — **1,304 deferred Stacks candidates** with reasons (862 inherited context, 439 structural, 3 classification). Supporting Pass 1/2 source evidence and Stacks contextual records remain under `harvest/`. Do not auto-promote them.
- `work/phase2-final-publication/BLOCKERS.json` and `REPORT.json` — retained publication diagnostics and counts.
- `work/phase2-final-publication/prototype_baseline.json` — essential original 20 theorems; required by the catalog builder.

## Routine development

**Publish and validate:** `python scripts/publish_phase2_catalog.py --all`, `python -m unittest discover -s tests -v`, `node --test tests/*.cjs`, `python scripts/build_site.py`. `.github/workflows/pages.yml` performs live deployment and refreshes the mathDef feed nightly. `.github/workflows/ui-search-tests.yml` checks the search UI.

**Add reviewed content:** Retain stable candidate IDs, original Stacks sources, exact mathematical hypotheses/conclusions, attribution and review status in the canonical master. The publisher regenerates the display catalog from that source. A candidate on hold stays out until its stated issue has actually been resolved.

**Discover new content:** Use the manual `harvest-stacks.yml` Pass 1 action and the retained `scripts/harvest_pipeline.py` toolkit. The scheduled `wikipedia-proof-dump.yml` crawl is separate: its code and results reside on the dedicated `work/wikipedia-theorem-harvest` and `data/wikipedia-proof-dump` branches. Do not interrupt its checkpointed ingestion.

Prior experiment and section-walk outcomes are preserved as source evidence in `harvest/`, but their one-time scripts and Actions have been retired from the production branch. Git history remains available for any historical reproduction. See `HARVEST_RUNBOOK.md` and `THEOREM_RECORD_CONTRACT.md` for current commands and schema.

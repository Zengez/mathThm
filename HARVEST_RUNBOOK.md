# mathThm acquisition and held-candidate runbook

Production canonical decisions are in `data/maththm_master.jsonl`; published presentation records are derived into `data/theorems.json`. This runbook describes **future additions and deferred candidates**, not a rerun of the completed 2026 Phase 2 review.

For a new Stacks source candidate, manually trigger `.github/workflows/harvest-stacks.yml` (bounded Pass 1). The maintained local tools are `scripts/harvest_stacks.py`, `scripts/harvest_pipeline.py`, `scripts/pass2_fast_stacks.py` and the core context/structure helpers still in `scripts/`. Inspect source assumptions and record editorial holds; Pass 1/2 processing alone never approves a theorem or a proof.

For the previous source corpus, the **protected deferral queue** is `harvest/problem_candidates.jsonl`. Its companion `PROBLEM_CANDIDATES_README.md` and manifest describe 862 source-context holds, 439 structural holds, and 3 uncertain classifications. The original `harvest/batches/*/pass1.jsonl` and `pass2.jsonl` files and context/section-walk artifacts are kept because they support that review. `python -m scripts.pass2_problem_candidates` rebuilds the deferred registry if canonical Pass 2 source decisions are updated; it does not approve them.

For reviewed source-equivalence decisions, update the canonical master with complete provenance and run `python scripts/publish_phase2_catalog.py --all` followed by `python -m unittest discover -s tests -v`. The publication script keeps approved results distinct from the remaining holds and does not claim proof screening where none was done. `work/phase2-final-publication/prototype_baseline.json` must remain present.

Wikipedia dump harvesting is intentionally separate from the Stacks workflow; the scheduled Action in `wikipedia-proof-dump.yml` checks out its crawler/results branches and is not part of the Pages catalog build.

Obsolete 2026 experimental workflow definitions and one-off section-walk scripts were removed from the active tree. Their commits remain recoverable from Git history if specialized retrospective reproduction is ever required.

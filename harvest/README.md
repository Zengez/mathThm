# Preserved Stacks candidate evidence

The site uses `data/maththm_master.jsonl` and its published catalog; these records are **not** reconstructed from historical batch files.

**Do not purge the deferred candidate evidence.** The unified `problem_candidates.jsonl` registry contains 1,304 unaccepted Stacks items with their exact original statements, source labels, pinned links, review rationale and context/structure classifications. `PROBLEM_CANDIDATES_README.md` and `PROBLEM_CANDIDATES_MANIFEST.json` document the counts. The canonical master separately retains 189 held source-equivalence decisions.

All historical `batches/` Pass 1/2 data, contextual indexes and section-walk source excerpts remain to support future review of these held items. Obsolete *executing* workflows and one-time scripts have been retired. For new harvesting, use the manual `harvest-stacks.yml` workflow or the core `scripts/harvest_pipeline.py` commands; for re-generating the unified deferral registry, run `python -m scripts.pass2_problem_candidates`.

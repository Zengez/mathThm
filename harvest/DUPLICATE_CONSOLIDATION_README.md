# Canonical theorem candidates — pre-Pass 3 duplicate consolidation

**Status (October 28, 2026):** Source-level duplicate adjudication finished for the 102 exact structured-statement match groups. This was a surface/context review, **not proof reading, truth verification, or a global semantic theorem equivalence audit**.

## Decision and counts

- Initial active Pass 2 structured population: **9,683** candidate IDs.
- **102** exact-structured-statement groups checked against original source text, source chapter and ambient category, explicit hypotheses/conclusions, references, and proof locators.
- **8** groups were confirmed to represent the same theorem in the same explicitly stated mathematical setting; those 16 source records now map to **8** canonical candidates.
- **94** groups were **not merged**. Source notation may be local, chapter-specific mathematical settings may differ (schemes vs algebraic spaces vs stacks, ringed sites vs schemes), or an exact semantic match has not been established. These remain active as separate theorems, not rejected candidates.
- New active canonical population: **9,675**. This is the count to use for Pass 3 and prototype-progress reporting.
- The **eight confirmed groups retain all 16 source citations and all 16 distinct proof URLs**, including eight alternate proofs that remain **uninspected**. No proof validity was inferred from matching source statements.

## Files and maintenance

- [ACTIVE_CANDIDATE_POOL.json](ACTIVE_CANDIDATE_POOL.json) — current active candidate count and merge metadata.
- [active_candidate_ids.jsonl](active_candidate_ids.jsonl) — canonical active IDs; merged aliases are not separate Pass 3 work items.
- [CONSOLIDATED_CANDIDATES.jsonl](CONSOLIDATED_CANDIDATES.jsonl) — one complete canonical statement/hypotheses/conclusions record per confirmed merge, with every original source and proof link.
- [DUPLICATE_CANDIDATE_CROSSWALK_2026-10-28.jsonl](DUPLICATE_CANDIDATE_CROSSWALK_2026-10-28.jsonl) — original candidate IDs (including canonical IDs) and their canonical destination, enabling later identity recovery.
- [DUPLICATE_ADJUDICATION_DECISIONS_2026-10-28.jsonl](DUPLICATE_ADJUDICATION_DECISIONS_2026-10-28.jsonl) — one reasoned *merge* or *keep separate* decision for each of the 102 detected groups.
- [DUPLICATE_MERGE_POLICY_2026-10-28.json](DUPLICATE_MERGE_POLICY_2026-10-28.json) — explicit, reviewed eight-group merge approval and category-sensitive exceptions.
- [DUPLICATE_GROUP_REVIEW_2026-10-28.jsonl](DUPLICATE_GROUP_REVIEW_2026-10-28.jsonl) — original-source and logical-structure comparisons that informed the decisions.
- [PASS3_PRECHECK_SURFACE_DUPLICATES_2026-10-28.json](PASS3_PRECHECK_SURFACE_DUPLICATES_2026-10-28.json) — earlier raw signals; **not** a current deduplicated active-candidate count.

Historical `harvest/batches/<batch>/pass1.jsonl` and `pass2.jsonl` were left untouched, so all candidate-specific research and original source provenance remains recoverable. The separate problem-candidate archive from the older Pass 2 campaign is also untouched.

## Important non-mergers

Identical prose can express different theorems. For example, statements that the composition of flat morphisms is flat appear in schemes, algebraic spaces, and stacks chapters, but have distinct underlying categories and proofs; they were not consolidated merely because the sentences matched. In another case, two copies of a formula involving `f_big` appear under **fppf** and **ph** topology-specific lemmas in the same chapter; their different source labels mean the ambient functor is not established to be identical. These were preserved separately.

## Next Pass 3

The canonical ID is the only active Pass 3 work item for a confirmed merged group. The primary proof is available for initial cursory screening. Additional source citations and proof URLs remain attached, but alternative proofs are marked `uninspected` until each is independently screened. Upon a later *plausible* provisional promotion, the accepted theorem record carries the `merged_candidate_ids`, `source_references`, and `proof_candidates` fields. Only the proof actually screened may be included in `proofs` with a screened status.

The publicly deployed theorem catalog (`data/theorems.json`) has **not** been changed by this merge. Pass 3 proof work has not yet been performed.

To deterministically rebuild the same canonical pool from its preserved source and policy:

```bash
python -m scripts.active_candidate_pool
```

See [consolidation workflow](../.github/workflows/consolidate-reviewed-duplicates.yml) for regression and provenance invariants. Further deduplication of semantically equivalent but differently worded theorems is a separate future audit, not part of this superficial pass.

# Derived — Chat Stage A source-first preparation (2026-10-31)

Branch: `work/phase2-stage-a-context-enrichment`. Pinned Stacks revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`.

## Complete chapter accounting

- **42 complete physical source sections**, §§1–42, source lines 17–12605.
- **38 candidate-bearing sections** and **4 context-only/no-active sections** (ordinals 1, 2, 3, 8).
- **217 original harvested candidate identities** for `derived.tex`, **199 active** and 18 nonactive skipped.
- **196 standalone-prepared** with Stage A decision `reconstruction_completed_awaiting_independent_stage_b_validation`; **3 further work needed** in §§32 and 34, retained as `stage_a_requires_standalone_expansion` and in the global hold registry. **0 independent Codex Stage B approvals** and **0 Phase 3 promotions** recorded by this run.
- 36 candidate-bearing sections entirely ready, 2 mixed/held sections; context-only sections counted separately.

## Bounded batches

- `batch_01_sections_01_15`: 15 physical sections, 75 active candidates, 75 ready, 0 held. Manifest and candidate overlay live together in `harvest/phase2_chat_stage_a/derived/batch_01_sections_01_15/`.
- `batch_02_sections_16_30`: 15 physical sections, 70 active candidates, 70 ready, 0 held. Manifest and candidate overlay live together in `harvest/phase2_chat_stage_a/derived/batch_02_sections_16_30/`.
- `batch_03_sections_31_42`: 12 physical sections, 54 active candidates, 51 ready, 3 held. Manifest and candidate overlay live together in `harvest/phase2_chat_stage_a/derived/batch_03_sections_31_42/`.

## Running scoped ledger

`CONTEXT_LEDGER.jsonl` has 67 source-anchored context events, including 42 definitions, 2 named Situations and labelled equations and precise source-prose notation; `SECTION_CHECKPOINTS.jsonl` has 42 post-section checkpoints. Each candidate is tied to a pinned source locator and section boundary. The named `situation-derived-functor` is expanded **only when expressly referenced**. Source-local definitions and prior results are not promoted to ambient assumptions; previous lemma/proposition hypotheses expire. The convention of small abelian categories at L3734 is recorded by its actual source introduction and guarded scope.

Follow-up audit materialized the explicitly cited localization factorization, canonical delta-functor construction, resolution-functor quasi-inverse, compact-generator tower, Brown representability predicates and Postnikov-system commuting diagram where source object correspondences were traceable. Separate conditional conclusions, existential witnesses, equivalence alternatives and internal enumerated grouping were preserved. An incorrect nested hypothesis/conclusion split in `lemma-products-sums-shifts-triangles` was corrected. Original source and historical drafts are preserved; proof bodies were not inspected.

## Held candidates — precise source blockers

- **§32 L9976** `lemma-unbounded-right-derived`: The pinned source's first cohomology-comparison clause uses an apparently malformed nested $H^i$ expression, `H^i(RF(\\tau_{\\leq a}E) \\to H^i(RF(E))`, and does not explicitly introduce all bounds a,b at their first use. Verify the intended induced truncation morphisms, parentheses, and quantifier scope before standalone promotion.
- **§32 L10102** `lemma-unbounded-left-derived`: The pinned source's left-derived analogue uses an apparently malformed nested $H^i$ expression, `H^i(LF(\\tau_{\\leq a+n-1}E) \\to H^i(LF(E))`. Verify the intended cohomology map and scope of indices a,b,n in each nested conclusion; do not silently repair source notation.
- **§34 L10588** `lemma-difficulty-K-injectives`: The inverse system $I_n^\\bullet$ depends on the detailed `lemma-special-inverse-system` construction, and the map $K^\\bullet\\to I^\\bullet$ is described by the source only as `(see proof)`. Its construction and comparison with the map into $R\\lim\\tau_{\\geq -n}K^\\bullet$ require independent source/object-map adjudication rather than importing proof-dependent data as Stage A context.

All three have their exact candidate ID, pinned URL, section ordinal, packet path and reason in `harvest/phase2_chat_stage_a/FURTHER_WORK_NEEDED.jsonl`.

## Validation and limits

Parsed all JSON/JSONL, checked 199 unique candidate IDs and complete consecutive section accounting, compared each manifest with reconstruction decisions, reconciled the global registry to the exact 3 holds, verified complete hypothesis/conclusion fields for all 196 ready records and balanced enumeration/equation environments, and scanned ready standalone statements for unexpanded source-local theorem/equation/Situation references and obvious anaphoric source dependencies (none found under the checked patterns).

**No independent mathematical equivalence or proof validation, no external regression suite or CI run, and no Phase 3 or production update** were performed. Stage A readiness is a source-first review gate for future independent Codex Stage B work, not mathematical approval.

Pinned source: https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/derived.tex

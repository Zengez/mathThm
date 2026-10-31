# Categories — Stage A chapter handoff

**Source:** [Stacks Project `categories.tex`](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/categories.tex), pinned revision `a04446e57ec1fbc252a871afcec7752fb2807b14`. **Branch:** `work/phase2-stage-a-context-enrichment`.

## Reconciled scope

- **44** source sections (lines **18–9856**), processed in order, including the context-only sections.
- **137** harvested statements; **125** active records, all reconciled once; **12** inactive records excluded from Stage A overlays.
- **118** records marked `reconstruction_completed_awaiting_independent_stage_b_validation` (not Stage B approved).
- **7** records marked `further_work_needed`; they are not in the Stage B-ready portion of this chapter.
- **44** source-order section checkpoints and **140** newly indexed context/notation lookup events across the batches.
- **0** proofs validated; **0** Stage B validations; **0** Phase 3 eligible.

## Batch packets

- 1. `harvest/phase2_chat_stage_a/categories/batch_01_sections_01_08/MANIFEST.json` — corresponding `RECONSTRUCTIONS.jsonl`, `CONTEXT_LEDGER.jsonl`, `SECTION_CHECKPOINTS.jsonl`, and hold sidecar when applicable.
- 2. `harvest/phase2_chat_stage_a/categories/batch_02_sections_09_18/MANIFEST.json` — corresponding `RECONSTRUCTIONS.jsonl`, `CONTEXT_LEDGER.jsonl`, `SECTION_CHECKPOINTS.jsonl`, and hold sidecar when applicable.
- 3. `harvest/phase2_chat_stage_a/categories/batch_03_sections_19_26/MANIFEST.json` — corresponding `RECONSTRUCTIONS.jsonl`, `CONTEXT_LEDGER.jsonl`, `SECTION_CHECKPOINTS.jsonl`, and hold sidecar when applicable.
- 4. `harvest/phase2_chat_stage_a/categories/batch_04_sections_27_34/MANIFEST.json` — corresponding `RECONSTRUCTIONS.jsonl`, `CONTEXT_LEDGER.jsonl`, `SECTION_CHECKPOINTS.jsonl`, and hold sidecar when applicable.
- 5. `harvest/phase2_chat_stage_a/categories/batch_05_sections_35_44/MANIFEST.json` — corresponding `RECONSTRUCTIONS.jsonl`, `CONTEXT_LEDGER.jsonl`, `SECTION_CHECKPOINTS.jsonl`, and hold sidecar when applicable.

## Section-context handling

Definition and example bodies are indexed as terminology/construction lookups only, never promoted into ambient hypotheses. The introductory filtered-system example at line 2914 is not a universal filteredness assumption for the later ind/pro statements. The category-over-category fibre-product model at line 6081 is an earlier, inactive source lemma used as a source definition/construction for the later fibre-product claims, not as inherited hypotheses. The fibred-category selected pullback arrows at line 6372 and pseudo-functor coherence are tracked separately. The monoidal unit-identification convention at line 9232 is a continuing **notational** convention, not a new algebraic assumption. The hypotheses of each candidate's own lemma, theorem or proposition are discharged on exiting that environment.

## Exact further-work registry

- **§22, line 3133: `lemma-characterize-essentially-constant-ind`** — Resolve the scope and existential quantification of X in clause (4), and its relationship to the cocone/value in the equivalence; source categories.tex:3133-3165. [Source](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/categories.tex#L3133), packet: `harvest/phase2_chat_stage_a/categories/batch_03_sections_19_26/MANIFEST.json`.
- **§22, line 3195: `lemma-characterize-essentially-constant-pro`** — Resolve the unbound X in condition (4), the cone/value scope, and the interpretation of the dual equivalences; source categories.tex:3195-3220. [Source](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/categories.tex#L3195), packet: `harvest/phase2_chat_stage_a/categories/batch_03_sections_19_26/MANIFEST.json`.
- **§25, line 3634: `lemma-a-version-of-brown`** — Specify which large categories and limits are admitted by the exact source size convention (remark-big-categories at line 77), without strengthening the source theorem. [Source](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/categories.tex#L3634), packet: `harvest/phase2_chat_stage_a/categories/batch_03_sections_19_26/MANIFEST.json`.
- **§25, line 3746: `theorem-adjoint-functor`** — Verify representability/solution-set size restrictions for big categories under remark-big-categories at line 77 before declaring the adjoint functor theorem standalone. [Source](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/categories.tex#L3746), packet: `harvest/phase2_chat_stage_a/categories/batch_03_sections_19_26/MANIFEST.json`.
- **§33, line 6419: `lemma-fibred`** — Check the pseudofunctor coherence diagrams and the precise chosen-pullback data from definition-functor-into-2-category (categories.tex:5243) and definition-pullback-functor-fibred-category (categories.tex:6392) before independent use. [Source](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/categories.tex#L6419), packet: `harvest/phase2_chat_stage_a/categories/batch_04_sections_27_34/MANIFEST.json`.
- **§35, line 7035: `lemma-fibred-groupoids`** — The final pseudofunctor claim relies on coherence from lemma-fibred at categories.tex:6419; a source-equivalent fully standalone formulation of that coherence remains to be established. [Source](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/categories.tex#L7035), packet: `harvest/phase2_chat_stage_a/categories/batch_05_sections_35_44/MANIFEST.json`.
- **§44, line 9763: `lemma-cat-dotted-arrows-composition`** — The existential D'' and its fibres refer to 'certain' solid squares and 'some choices' without specifying the construction in this source statement. Reconstruct the exact category and comparison functor from source definitions before treating as standalone. [Source](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/categories.tex#L9763), packet: `harvest/phase2_chat_stage_a/categories/batch_05_sections_35_44/MANIFEST.json`.

The same seven entries are present in the shared `harvest/phase2_chat_stage_a/FURTHER_WORK_NEEDED.jsonl` registry and in the corresponding batch sidecars. These entries are not to be silently reclassified as standalone-ready without a new Stage A review.

## Structural regression (Chat-side)

Verified unique active candidate IDs and complete source-ordered coverage, full section checkpoint range and cross-batch line adjacency, parsable JSON/JSONL, no stray `\\ref{...}` in Stage B-prepared statement text, nonempty hypothesis/conclusion arrays, no unknown context IDs, and all proof/independent-validation/Phase-3 flags false. Corrected an empty hypothesis array, one batch-boundary checkpoint, and three context references during final QA. The repository's full command-line regression suite was **not** run here; independent Stage B mathematical verification remains necessary.

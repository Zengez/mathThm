# Standalone theorem-context pilot — bounded first pass (2026-10-28)

Pinned Stacks source revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`.

**Status:** The new lightweight source index has been used on a small deterministic sample of **19 canonical candidates**, spanning **17 source chapters**. **14/14 explicitly referenced source labels** in these packets resolved to exact pinned source positions. This is a context-reconstruction pilot; no proof correctness, theorem truth, or final Pass 3 eligibility determination was performed.

## What was reviewed

- **11** candidate-specific standalone-context screens were annotated using the bounded introductory excerpts, reviewed convention atlas, existing Pass 2 data, and a few exact local source passages.
- **8** provisional duplicate group representatives received preliminary mathematical-context comparisons. The mergers have **not** been reapproved or revoked by this pass.
- **6** candidates have proposed explicit hypothesis language, including one concrete missing section-level hypothesis and one short ring-theoretic restatement. Proposals have not overwritten Pass 2 or the canonical corpus.
- **0** standalone candidate records were finally approved as publishable; **0** proofs screened.

## Useful observations

1. **Source situations already recovered in Pass 2 are not necessarily standalone.** Theorems may still depend on a separate named definition, an unexplained numerical condition, or notation defined in a remark.
2. **Moduli (`moduli.tex`, candidate `candidate.stacks.0cb48412cebcc4d577f50f96`):** The phrase “as in the introduction to this section” hides that `f:X -> B` is a **separated morphism of algebraic spaces of finite presentation**. This appears in the section opening, not in the existing copied Situation.
3. **Chow Homology (`chow.tex`):** Named Situation `situation-setup` yields precise assumptions on `S` and its dimension function. Pass 2 included the original setup, but still needs a concise standalone rewrite and an explicit explanation of `Z_k(Y)`.
4. **Varieties (`varieties.tex`):** Named Situation `situation-glue` is readily replaceable by explicit hypotheses about a field `K`, subrings `A,B`, `R=A ∩ B` and `B` being a valuation ring. The chapter-wide ground-field letter `k` does not belong in this purely ring-theoretic result.
5. **Formal Spaces (`formal-spaces.tex`):** The context lookup correctly distinguishes a theorem before the new conventions introduced at line 620 from one after it. The later theorem explicitly depends on the source's formal-algebraic-space definition, which includes an additional set-theoretic condition.
6. **Étale (`etale.tex`):** Noetherian hypotheses are explicitly repeated in the original theorem, consistent with the chapter's warning; no general Noetherian hypothesis should be invented.
7. **Stacks valuation criterion (`stacks-morphisms.tex`):** A named source definition includes nontrivial 2-morphism compatibility conditions. It should not be flattened into a diagram with ordinary commuting arrows.
8. **Provisional duplicate groups:** Context may match at the headline level even when local constructs such as the naive cotangent complex need separate matching. **All eight mergers remain provisional** until the standalone expansions are complete.

## What the 19-record review files do and do not mean

The [pilot packets](standalone_context_pilot_2026-10-28_packets.jsonl) capture the original Pass 1 and Pass 2 statements, actual source line/section, chapter/section opening snippets, exact named source references and convention leads. The [first review notes](standalone_context_pilot_2026-10-28_first_review.jsonl) give one bounded human-readable contextual finding per candidate, including proposed hypothesis language and any remaining unresolved local notation.

The hypothesis proposals are **not** certified mathematically equivalent canonical records. They are editorial drafts to be checked against the original source and mathDef conventions when that candidate is processed. Any cited earlier theorem is a proof dependency, not automatically an additional assumption.

## Next work: per-candidate, not more infrastructure

The standing convention atlas and the two small source locators are sufficient to begin systematic standalone reconstruction. Use the same bounded approach as the pilot: apply explicit scope, inspect only source references relevant to understanding the theorem, expand missing hypotheses, and mark unresolved cases. Do **not** build a full chapter-wide assumption timeline or recursively research every referenced mathematical definition.

All source Pass 1/2 records, the active canonical intake, previously combined proof/source citations, and the public theorem catalog remain unchanged.

## Index files

- [Mechanical section openings](stacks_context_openings_2026-10-28.jsonl)
- [Exact Stacks source labels](stacks_context_labels_2026-10-28.json)
- [Index metrics](stacks_context_light_index_manifest_2026-10-28.json)
- [Standing convention atlas](stacks_standing_context_atlas_2026-10-28.jsonl)

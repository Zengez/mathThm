# Standalone theorem expansion — first bounded batch (2026-10-28)

**Scope:** Actual Pass 2 standalone-context reconstruction using the pinned Stacks revision `a04446e57ec1fbc252a871afcec7752fb2807b14`, the [55-section standing conventions atlas](stacks_standing_context_atlas_2026-10-28.jsonl), the [3,288 section-opening previews](stacks_context_openings_2026-10-28.jsonl), and the [21,297 exact labels](stacks_context_labels_2026-10-28.json).

**This is a mathematical source-context review, not proof verification.** No theorem candidates were published, no source Pass 1/2 files or original source citations were changed, and no Pass 3 proof screening was performed.

## Results

| Status | Candidates | Meaning |
|---|---:|---|
| Standalone source context validated | **5** | The full rewritten hypotheses/conclusions were compared with their pinned original Stacks source and are judged to preserve the meaning and scope; **not** a proof-verification verdict |
| Standalone draft ready for further validation | **1** | Complete explicit wording drafted, but source terminology still needs targeted confirmation |
| Further contextual reconstruction required | **7** | A concrete missing definition, notation, assumption or construction is recorded, so not yet standalone |
| **Total** | **13** | Across **8** previously provisional merger groups plus five other working candidates |

**Validated source-context statements:**

- [Valuation-ring unit dichotomy](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/varieties.tex#L7304-L7317): explicitly quantifies common fraction field `K`, two subrings `A,B`, `R=A∩B`, and valuation-ring hypothesis.
- [Formally étale iff formally smooth and formally unramified](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/more-morphisms.tex#L3129-L3134): the source explicitly concerns **schemes**, despite one occurrence being in a chapter about algebraic spaces.
- [Étale morphisms of algebraic spaces survive base change](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/spaces-morphisms.tex#L7749-L7753): rewrites the implicit universal statement with an arbitrary base, object maps and fiber-product projection.
- [Composition of étale algebraic-space morphisms](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/spaces-properties.tex#L2163-L2167): specifies composable `X→Y→Z` explicitly.
- [Flat-surjective descent of regularity for algebraic spaces](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/spaces-descent.tex#L924-L929): preserves exactly the lfp, flat, surjective and regular hypotheses, without importing a scheme-only ambient or an unnecessary additional Noetherian condition.

**One remaining clean draft:** The regular-alteration theorem's local-ring data and four conclusions are rewritten with distinct symbols for the alteration and a nonzero localization element. Before final sign-off, check the source's meaning of *alteration* and *generic formal fibre*.

**Seven held for targeted source-context work:** Pseudo-coherent homotopy colimits; two theorems using the naive cotangent complex (a shared terminology issue); finite-flat cycle push-pull over a base with dimension function; equivalence of two unramifiedness definitions; numerical invariants of coherent-sheaf stacks; and thickenings of affine formal algebraic spaces.

## What this tested about the atlas

The source index quickly located the standing assumptions in a *named Situation* and made section-level assumptions visible without searching an entire chapter. It also prevented bad inheritance: the scheme/algebraic-space ambient, and mid-chapter context changes, are recorded separately.

The smallest high-leverage next candidate-specific lookup is probably the precise **naive cotangent complex** definition: resolving this one issue may advance two of the seven blocked theorem statements. The remaining blockers should be addressed locally and deferred if they require substantial mathematical research.

This **13-item sample was intentionally context-heavy and duplicate-focused**, so the fraction validated is not an estimate of the success rate across the 9,675 active candidates.

## Auditable files

- [All 13 reconstructed source-context records](standalone_candidate_expansion_batch01_2026-10-28.jsonl) — statements, hypotheses, conclusions, source links, semantic scope checks, unresolved issues, group aliases and review status.
- [Integrity/validation manifest](standalone_candidate_expansion_batch01_2026-10-28_manifest.json) — counts, preserved source occurrences and proof-screening safeguards.
- [Earlier 19-candidate trial](standalone_context_pilot_2026-10-28_summary.md) — how sample candidates were selected.

## Next steps

Continue in small batches, using the existing atlas rather than expanding it. Validate *mathematical source equivalence* separately from *proof plausibility*; track individual blockers explicitly; reconsider the eight provisional source merges after both source contexts have been reconstructed; and prevent canonical promotion until the standalone gate is satisfied. The existing active pool remains **9,675**, and no candidate was enabled for Pass 3 in this batch.

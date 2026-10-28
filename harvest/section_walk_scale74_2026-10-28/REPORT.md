# Complete-section scaling trial — 74 candidates

**Date:** October 28, 2026  
**Project:** mathThm, independent Stacks candidate intake  
**Pinned Stacks revision:** `a04446e57ec1fbc252a871afcec7752fb2807b14`

## Overall outcome

The requested step-up from a 30-candidate pilot to **approximately 75** has now been completed, without dividing any Stacks source section. The actual count was **74 active canonical candidates in 5 entire source sections** from `morphisms.tex`, spanning **2,305 source lines** in total.

| Section | Source line interval | Active candidates | Draft ready for validation | Context still required |
|---|---:|---:|---:|---:|
| Affine morphisms | 1710–2110 | 13 | 11 | 2 |
| Quasi-finite morphisms | 3522–4053 | 17 | 16 | 1 |
| Syntomic morphisms | 5718–6136 | 14 | 10 | 4 |
| Sheaf of differentials of a morphism | 6337–6858 | 15 | 14 | 1 |
| Unramified morphisms | 7603–8033 | 15 | 14 | 1 |
| **Total** | **5 whole sections** | **74** | **65** | **9** |

**Semantics of "draft ready":** hypotheses and conclusions were individually reconstructed, the relevant source definition and scope were considered, and no currently identified source-specific context blocker remains. This is **not a final mathematical equivalence certificate, proof verification, or Pass 3 promotion**. All 74 candidates are still in an independent review overlay, and **0 have received final sign-off in this scaling pass**.

## What the complete-section method actually did

1. Grouped the 9,675-candidate active pool by original source section. Selected five complete, candidate-rich sections of one chapter (not exactly 75 and not split mid-section).
2. Walked source environment events in line order through each section; did not read proof bodies. Validated **84 paired enter/exit environment events**, including **75 source lemma environments**.
3. Matched and reconstructed **74 active candidate lemmas**. The Unramified section contains one more lemma (at `morphisms.tex:7789`) that is not in the currently active candidate population. Its source scope was traversed, but no new candidate was invented or promoted.
4. Interpreted relevant definitions for affine, quasi-finite, syntomic, relative differential, and unramified morphisms **once per section** as available terminology, not as extra standing hypotheses. Local conditions from each lemma expire at the end of that lemma.
5. Reviewed an explicit [mid-section notation override at line 6404](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/morphisms.tex#L6404) in the Differentials section: from that source point forward, `Ω_{U/S}` and `Ω_{U/V}` may denote the identified restriction `Ω_{X/S}|_U`. This is **notation**, not an assumption, and must **not** be applied to the two candidates preceding it.
6. Preserved source multi-condition equivalences, dual forms such as *unramified versus G-unramified*, addenda and theorems with several separate implications in structured conclusion fields.
7. Created **five section-completion checkpoints**, after the actual full section intervals, with the completed active IDs, named reference definitions and an **empty surviving lemma-local context**.

Source-of-truth artifacts: [five-section intake manifest](MANIFEST.json), [validation counts](VALIDATION.json), and [section-completion checkpoints](SECTION_CHECKPOINTS.jsonl).

## Nine candidates with targeted context holds

| Section | Candidate label | Missing or potentially ambiguous context |
|---|---|---|
| Affine | `lemma-characterize-affine` | Canonical relative Spec identification and notation |
| Affine | `lemma-get-affine` | Exactly which space supplies the closedness condition for `j(Y)∩Z` |
| Quasi-finite | `lemma-base-change-quasi-finite` | Scheme-theoretic fibre product versus point-set inverse image for quasi-finite loci |
| Syntomic | `lemma-local-complete-intersection` | Global complete intersection and regular-sequence conventions |
| Syntomic | `lemma-syntomic-locally-standard-syntomic` | Source-defined complete-intersection local-ring criterion |
| Syntomic | `lemma-set-points-where-fibres-lci` | Fibre local complete intersections and syntomic-locus openness |
| Syntomic | `lemma-standard-syntomic-relative-dimension` | Relative global complete-intersection regular-sequence convention |
| Differentials | `lemma-two-immersions` | Natural conormal functoriality morphism |
| Unramified | `lemma-unramified-at-point` | Distinction between ordinary unramifiedness and G-unramifiedness in fibre characterization |

Four holds share **one mathematical family**, complete-intersection terminology. Resolving a single rigorously documented definition family later may efficiently unblock several candidates. These were **not researched recursively** during this scaling test.

## Practical cap observations

The 74-candidate run completed and passed all structural, source-ID, scope and Python-regression checks; no section was split, and no candidate was lost or double counted. This is a concrete demonstrated **batch capacity of at least 74 drafts**, *not* an established maximum throughput or safe cap for mathematical verification.

This run concentrated five medium-length sections in **the same chapter**, but **they were not consecutive sections**: no unreviewed intervening section was silently treated as established standing context. Context is local to the source section, supplemented only by explicitly relevant chapter conventions and source references.

The previous pilot produced 30 drafts across two sections (779 source lines). This pilot produced 74 across five (2,305 source lines). There is no controlled wall-clock A/B measurement, and substantial candidate-specific terminology may increase review cost in other chapters. We should measure those effects before claiming linear scaling or choosing an optimal cap.

**Recommended next trial:** increase moderately to about **100–120 active candidates**, again selecting **complete source sections** only. Prefer adjacent sections when possible. Preserve a strict distinction between work in each layer: *source grouping / scope traversal*, *standalone mathematical draft*, *final context equivalence validation*, and *proof screening*. If a section is unusually complex, complete the entire section while leaving its individual hard theorems in a documented hold state rather than performing unbounded mathematical research.

## Files

- [Affine candidate drafts](affine_reviews.jsonl) and [source packets](affine_packets.jsonl)
- [Quasi-finite candidate drafts](quasi_finite_reviews.jsonl) and [source packets](quasi_finite_packets.jsonl)
- [Syntomic candidate drafts](syntomic_reviews.jsonl) and [source packets](syntomic_packets.jsonl)
- [Differentials candidate drafts](differentials_reviews.jsonl), [scoped notation review](differentials_scopes.json), and [source packets](differentials_packets.jsonl)
- [Unramified candidate drafts](unramified_reviews.jsonl) and [source packets](unramified_packets.jsonl)
- [Five section completion checkpoints](SECTION_CHECKPOINTS.jsonl)
- [Validation manifest](VALIDATION.json)

## Integrity boundaries

Original Pass 1 and Pass 2 candidate sources, the active 9,675-ID pool, the eight provisional duplicate mergers, proof citations, and the published mathThm theorem catalog were not edited. **Zero candidates were approved for Pass 3 or published.** The source-specific review overlays and efficient scoping workflow are the only products of this trial.

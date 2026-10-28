# Scaled consecutive-section theorem reconstruction: 150 candidates

**Date:** October 28, 2026  
**Project:** Zengez/mathThm  
**Pinned Stacks revision:** `a04446e57ec1fbc252a871afcec7752fb2807b14`

## Result and limits

**Exactly 150 new active canonical candidates were processed in 19 physically consecutive, complete sections of `algebra.tex`, source lines 4284–10036 (5,753 lines).** This falls within the user's requested 150 ±10 range, without splitting a section or reusing any sections from the earlier 30- and 74-candidate pilots.

- **150:** separate source-faithful standalone editorial draft records, each containing the complete original source statement, normalized independently readable display statement, structured hypotheses and conclusions, local scope, source provenance, and references to relevant encountered definitions.
- **134:** no currently known source-specific blocker in the editorial reconstruction; ready for **a separate mathematical source-equivalence review**. **Not** already validated for mathematical equivalence or proof correctness.
- **16:** individually identified contextual or structural issues remain open; each has an explicit hold note in its candidate record.
- **0:** final standalone-equivalence approvals, proof reviews, Pass 3 eligibilities, and published theorem promotions in this campaign.

The initial mechanically obtained 132-ready/18-held split was revised after hand-targeted mathematical and structural cleanup. The **final audited status is 134 ready / 16 held**.

## Every consecutive source section (including zero-active section)

| No. | Stacks source section | Active candidates | Draft-ready | Context-held | Physical source lines |
|---:|---|---:|---:|---:|---:|
| 1 | Glueing functions | 4 | 3 | 1 | 4284–4535 |
| 2 | Zerodivisors and total rings of fractions | 4 | 3 | 1 | 4536–4655 |
| 3 | Irreducible components of spectra | 4 | 3 | 1 | 4656–4815 |
| 4 | Examples of spectra of rings | 0 | 0 | 0 | 4816–5088 |
| 5 | A meta-observation about prime ideals | 6 | 6 | 0 | 5089–5370 |
| 6 | Images of ring maps of finite presentation | 10 | 10 | 0 | 5371–5720 |
| 7 | More on images | 8 | 6 | 2 | 5721–5979 |
| 8 | Noetherian rings | 10 | 10 | 0 | 5980–6237 |
| 9 | Locally nilpotent ideals | 6 | 5 | 1 | 6238–6444 |
| 10 | Curiosity | 2 | 1 | 1 | 6445–6519 |
| 11 | Hilbert Nullstellensatz | 1 | 1 | 0 | 6520–6648 |
| 12 | Jacobson rings | 14 | 10 | 4 | 6649–7433 |
| 13 | Finite and integral ring extensions | 22 | 21 | 1 | 7434–7970 |
| 14 | Normal rings | 14 | 13 | 1 | 7971–8338 |
| 15 | Going down for integral over normal | 6 | 5 | 1 | 8339–8586 |
| 16 | Flat modules and flat ring maps | 19 | 17 | 2 | 8587–9306 |
| 17 | Supports and annihilators | 7 | 7 | 0 | 9307–9513 |
| 18 | Going up and going down | 10 | 10 | 0 | 9514–9905 |
| 19 | Separable extensions | 3 | 3 | 0 | 9906–10036 |
| | **TOTAL** | **150** | **134** | **16** | **4284–10036** |

The fourth source section (“Examples of spectra of rings”) contains **zero** active candidates. It was still traversed and checkpointed. No empty section was silently omitted from the contiguous sequence.

## Shared context and bidirectional scoping results

- All **189** source formal-environment frames opened and closed; candidate-local hypotheses were discarded on exit rather than leaking into following statements. **6** additional nonactive formal statement environments were traversed but not added to the active pool.
- **14** named source definitions were captured with pinned labels and exact source lines. They are usable as **mathematical definitions**, not automatically inserted as new hypotheses. They remain available across subsequent consecutive sections.
- The two prose signals were reviewed: “Let us give some examples of Oka families” (line 5143) is editorial, and the general prime-specialization correspondence (line 9518) is expository topological interpretation. **Neither introduces a standing theorem hypothesis.**
- Chronological distinctions were maintained: *normal domain* enters at line 7978; *normal ring* enters only at line 8205. Likewise, the Oka-family definition enters at line 5134 and is **not** retroactively available to an earlier lemma.
- The only exception to the overall commutative-ring convention in these candidates, a theorem permitting **a possibly noncommutative algebra**, was explicitly preserved.
- **19** completed-section checkpoints store all processed active IDs, real source ends, next-resume source positions, and cumulative available definitions, with **no local lemma assumptions carried over**.
- **157** proof environments were skipped as proof material (no proof screening).

The source passage corpus is [SHARED_CONTEXT_EXCERPTS.jsonl](SHARED_CONTEXT_EXCERPTS.jsonl); semantic scope decisions are [SCOPES_REVIEWED.json](SCOPES_REVIEWED.json); the complete source event/packet materials are stored as `s01_` through `s19_` artifacts.

## Logical-structure corrections

One useful audit finding was that an older Pass 2 split occasionally treated alternatives in a theorem's *equivalence* as if they were global hypotheses. The source-first draft builder now has distinct paths for:

- Equivalent conditions (each condition remains part of the conclusion, while only the theorem's actual ambient assumptions become hypotheses).
- Independently quantified assertions or implications (each clause retains its own antecedent).
- Multiple clauses constraining **one existentially quantified witness** (the witness conditions stay grouped).
- Source clauses after an enumeration, such as an additional “Moreover” statement, which are preserved separately.

Bounded mathematical examples corrected during this pass include the second conclusion of the minimal-prime/reduced-ring lemma, the full Oka-family assumption, a source-dependent symbol `X` replaced with `Spec(R)` in a quasi-compact-open characterization, and clean source-reference wording in several algebraic statements.

These corrections improve the editorial reconstruction, **but no claim is made that every one of the 150 source statements has received final semantic-equivalence or proof verification**. The original source and both Pass 1/2 layers remain unchanged.

## Remaining 16 issues

The held candidates are explicitly listed in their section review files. Representative themes include:

- A source-defined “trivial relation” for flat modules, which requires exact logical quantifiers.
- Irreducible-component and Jacobson-topological-space definitions supplied outside these sections.
- A grouped existential characterization of non-Jacobson rings.
- Some subtle localization, maximal-ideal, integral-closure and ring-product statements requiring source-faithfulness review.
- A large four-way flatness equivalence and a polynomial-divisibility theorem with differently quantified subring conclusions.

These are bounded individual candidate holds. We **did not** turn the preparatory context resource into a separate recursive mathematics-research effort.

## What this tells us about batch sizing

The previous demonstration completed **30 drafts in two source sections** and then **74 in five nonconsecutive sections**. This round demonstrates **150 editorial drafts in 19 complete consecutive sections**, over **5,753 physical source lines**.

**150 is therefore a demonstrated feasible *source-context reconstruction/drafting* batch size**, not yet a validated upper cap for full mathematical equivalence review or proof screening. There is no controlled wall-clock comparison across the pilot runs; the mathematics and fraction of hard candidates vary.

A reasonable next experiment, if the user wants to continue increasing, is approximately **200–225 candidates in consecutive complete sections**, retaining the same separate final mathematical-equivalence and Pass 3 gates. A quality review of some of these 134 ready drafts is worthwhile before treating the 150-candidate drafting rate as sufficient for automatic corpus promotion.

## Files and tests

- [Source intake manifest](MANIFEST.json): full selected 19-section source range and 150 canonical IDs.
- [Draft manifest](DRAFT_MANIFEST.json): audited per-section count and draft-status breakdown.
- [Validation metrics](VALIDATION.json): scope, chronological definitions, source integrity and logical-structure controls.
- [Completed-section checkpoints](SECTION_CHECKPOINTS.jsonl): safe section-end resume states.
- [Local mathematical contexts](SHARED_CONTEXT_EXCERPTS.jsonl) and [scope adjudications](SCOPES_REVIEWED.json).
- Individual candidate drafts: `s01_reviews.jsonl`, ..., `s19_reviews.jsonl`, with original packets and events alongside each.
- Code: `scripts/stacks_consecutive_section_window150.py`, `scripts/stacks_section_walk_scale150.py`, `scripts/stacks_section_walk_scale150_reconstruct.py`, `scripts/validate_stacks_section_walk_scale150.py`.
- [Successful pinned-source traversal](https://github.com/Zengez/mathThm/actions/runs/40777786302) and [successful final source-scope/regression validation](https://github.com/Zengez/mathThm/actions/runs/40779567702).

**Integrity gate:** all original Pass 1/2 candidate files, the active 9,675-candidate source pool, earlier provisional duplicate decisions, and the public theorem catalog remain unchanged; 0 proof reviews and 0 Pass 3 approvals.

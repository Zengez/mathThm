# Scoped chapter/section walkthrough — first two-section pilot

**Date:** October 28, 2026  
**Pinned source:** `a04446e57ec1fbc252a871afcec7752fb2807b14` (Stacks Project).  
**State:** Source-ordered standalone reconstructions saved as review overlays. No proof screening or publication.

## Result

| Item | Observed |
|---|---:|
| Active canonical candidates grouped by their source section | **9,675 of 9,675** |
| Populated source sections | **2,320** |
| Source sections with eight or more active candidates | **298** |
| Sections fully swept in this pilot | **2** |
| Source lines in those sections | **779** |
| Candidates with individually drafted standalone hypotheses/conclusions | **30** |
| Shared context records explicitly interpreted | **2** |
| Reuse opportunities for those two records | **28** |
| Candidate-local lemma frames pushed and popped | **30** |
| Restorable after-lemma context checkpoints | **30** |
| Proofs reviewed | **0** |
| Drafts with final source-equivalence approval / Pass 3 eligibility | **0 / 0** |

Source grouping and candidate counts are from [section ranking](SECTION_WALK_PILOT_RANK_2026-10-28.json). The reconstruction figures are from the two audited reviews and their linked checkpoint files.

## Section 1: Morphisms — Flat morphisms

- Source interval: [`morphisms.tex` lines 4615–4994](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/morphisms.tex#L4615-L4994).
- **15** candidate lemmas.
- A single [definition of flatness](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/morphisms.tex#L4639-L4655) is available to all 15 statements. It is reused as *terminology*, never as an automatic additional hypothesis.
- There are **zero** new standing section assumptions in the source. Each lemma's locally quantified schemes, points, sheaves, flatness conditions, and auxiliary symbols expire at the corresponding `\end{lemma}`.
- All **15** original statements were reconstructed into explicit hypotheses and conclusions; the two substantial four-way characterizations of flatness were kept as equivalences, not incorrectly split into independent hypotheses.
- Confirmed **15 local lemma frame pushes and 15 pops**; **14 shared-definition reuse opportunities**; **15 post-lemma checkpoints**.

See [15 standalone drafts](SECTION_WALK_PILOT_STANDALONE_REVIEWS_2026-10-28.jsonl), [source-order event stream](SECTION_WALK_PILOT_EVENTS_2026-10-28.jsonl), [context checkpoints](SECTION_WALK_PILOT_CONTEXT_CHECKPOINTS_2026-10-28.jsonl), and [validation metrics](SECTION_WALK_PILOT_VALIDATION_2026-10-28.json).

## Section 2: Limits — Descending properties of morphisms

- Source interval: [`limits.tex` lines 1729–2127](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/limits.tex#L1729-L2127).
- **15** candidate lemmas.
- The section explicitly declares "**We will work in the following situation**," followed by a [named Situation](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/limits.tex#L1733-L1747). Each one of the 15 candidate theorems explicitly invokes that Situation. This is a **positive standing-context declaration**.
- The situation fixes a directed inverse system of schemes with affine transitions, their limit `S`, a base-stage morphism `f_0:X_0→Y_0`, quasi-compact/quasi-separated objects, and all its base changes `f_i` and `f`.
- Only the ambient Situation persists across lemmas. The further hypothesis on `f_0` varies between candidates: **2 with no additional finiteness condition**, **5 locally of finite type**, and **8 locally of finite presentation**.
- **All 15** have complete expanded standalone draft statements (the full fixed setup is written in every materialized statement). Local finiteness assumptions were explicitly checked against their own source statements and popped before the next lemma.
- The distinction matters: for example, the finite-morphism descent lemma requires `f_0` locally of finite type; the later separated-morphism descent lemma does **not** inherit that restriction.

See [adjudicated shared Situation](SECTION_WALK_PILOT_LIMITS_SHARED_CONTEXT_2026-10-28.json), [15 standalone drafts](SECTION_WALK_PILOT_LIMITS_STANDALONE_REVIEWS_2026-10-28.jsonl), [source-order events](SECTION_WALK_PILOT_LIMITS_EVENTS_2026-10-28.jsonl), [context checkpoints](SECTION_WALK_PILOT_LIMITS_CONTEXT_CHECKPOINTS_2026-10-28.jsonl), and [validation metrics](SECTION_WALK_PILOT_LIMITS_VALIDATION_2026-10-28.json).

## What worked

The efficient unit is **a source-ordered sequence of candidate theorems in a section**, not a candidate in isolation. A simple event view (enter/exit named formal environments, possible standing-context prose, candidate starts, proof spans) reveals where mathematical state may enter and leave. A bounded human/model scope adjudication determines which ambient declarations really persist.

A *compiler-like scope stack* is a useful mental model: lemma-local assumptions are pushed only for that lemma and popped when it ends. Definitions and named situations remain addressable as references; only an explicitly justified ambient declaration becomes persistent mathematical context. The final theorem record must materialize its own complete hypotheses, even if the interpretation was cached and reused.

The initial mechanical scan therefore does **not** need to read or interpret every paragraph or every proof. It can visit source structure once and inspect only context-bearing prose plus the actual candidate statements. Exact label locations handle named dependencies without re-searching entire chapters. Checkpoints now store the real `\end{lemma}` source line and the next safe resume line.

## Limitations and remaining gates

- **Thirty drafted does not mean thirty verified theorems.** The reconstruction records are source-faithful *drafts* awaiting a separate final equivalence/definition-link review, with Pass 3 explicitly disabled. No proof correctness was evaluated.
- The two selected sections are relatively regular, with one salient shared definition/Situation each. This is a qualitative demonstration, **not a controlled benchmark** against the previous independent 13-candidate trial. No reliable wall-clock speedup was measured.
- The next scope regression tests should include a section with **a standing context introduced or withdrawn partway through a section**, or multiple nested context changes. Our current two test sections exercise local add/pop and section-long persistence, but not every possible source scoping convention.
- A reference environment appearing before a lemma is not automatically an applicable hypothesis. The source's explicit prose and per-lemma citations supplied the necessary evidence for the Limits Situation. In less explicit cases, a human/model reviewer must make that decision.
- The Stacks global conventions atlas and the chapter/section openings remain available. We should now **stop building general infrastructure** and process new sections in bounded batches, adding only narrowly justified context events and regression cases when an actual failure is found.
- All original Pass 1/2 records, canonical active IDs, provisional duplicate mergers, published theorem data and proof citations remain unchanged.

## Reproduction

The source-group rank and source-order packets are produced by `scripts/stacks_section_walk_pilot.py`, using the pinned Stacks checkout. The two audit/checkpoint scripts are `scripts/validate_section_walk_pilot.py` and `scripts/validate_section_walk_limits.py`. Test/validation workflows are [Flat morphisms](https://github.com/Zengez/mathThm/actions/workflows/run-stacks-section-walk-pilot.yml) and [Limits](https://github.com/Zengez/mathThm/actions/workflows/validate-stacks-section-walk-limits.yml).

**Next candidate processing recommendation:** prioritize candidate-rich sections, sweep their context once, maintain scope accurately through each environment, materialize complete theorem statements, and checkpoint after each completed lemma. Group multiple short sections into one batch when comfortable; split longer sections at these same safe boundaries. Do not recursively expand terminology irrelevant to the selected theorems.

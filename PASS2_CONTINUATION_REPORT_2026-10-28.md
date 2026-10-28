# mathThm — Stacks Pass 2 continuation report (October 28, 2026)

## Scope and verified status

The user requested continued Pass 2 work on the remaining Stacks Project candidates, with source-faithful hypotheses/conclusions and unresolved or structurally difficult records preserved. All three independently collected Pass 1 batches were covered.

**Before this continuation:** 10,987 candidate statements; 8,373 Pass 2 resolved; 640 needing structural interpretation; 1,971 needing context; 3 needing classification. **After this continuation:** **9,383 Pass 2 resolved; 502 needing structure; 1,099 needing context; 3 needing classification**. Thus **1,010 additional Pass 2 source statements were structured**, leaving **1,604 still open**. This is **85.4%** of the original 10,987 candidate statements with recorded Pass 2 hypotheses/conclusions; it is NOT the number of mathematically verified theorems.

| Harvest | Candidate statements | Pass 2 resolved | Needs structure | Needs context | Needs classification |
| --- | ---: | ---: | ---: | ---: | ---: |
| First bulk | 1,100 | 1,005 | 37 | 58 | 0 |
| Second bulk | 2,022 | 1,807 | 54 | 161 | 0 |
| Remaining chapters | 7,865 | 6,571 | 411 | 880 | 3 |
| **All three** | **10,987** | **9,383** | **502** | **1,099** | **3** |

## Work completed in this continuation

1. **495 new splits** from exact, pinned Stacks *Situation* labels in the same source file. Source environment text and revision provenance were kept with each decision. Workflow: [Pinned source Situation recovery](https://github.com/Zengez/mathThm/actions/runs/40736521578).
2. **164 new splits** after distinguishing bibliographical/definitional citations and self-contained diagrams from genuine unprovided standing assumptions, plus a limited number of locally recoverable source-lemma setups. Workflow: [Secondary source-context analysis](https://github.com/Zengez/mathThm/actions/runs/40737327102).
3. **138 new splits** with source-faithful deeper structural recognition: explicit setup and existential statement, list-of-cases logical form, scoped equivalence addenda, reversed conditional *P if Q*, and multi-assertion cases. Workflow: [Deeper structural Pass 2](https://github.com/Zengez/mathThm/actions/runs/40737921373).
4. **213 new splits** from embedded named Situation references, including situations introduced inside Let statements and source statements with explicit top-level Then or enumerated conditional clauses. Workflow: [Embedded Situation continuation](https://github.com/Zengez/mathThm/actions/runs/40738717391).

All four successful runs ran the Python regression suite and validated record completeness, proper dual-column indexing of equivalent conditions, and no Pass 3 entries. Exploratory and failed workflow attempts, including corrections to regression tests, were superseded by these successful runs and **are not included in the totals**.

**Important distinction:** All new resolutions are provisional source-level interpretations, not independent verification that a theorem is mathematically true or that an attached proof is correct. The user's settled mathThm equivalence rule was maintained: every equivalent condition is searchable in both hypothesis and conclusion fields, while keeping one canonical theorem statement.

## Durable recovery sources

- The source of truth is always each batch's `pass2.jsonl` alongside its original `pass1.jsonl`.
- The combined, machine-checked counters and flagged classification items are in [harvest/PASS2_RESUME_INVENTORY_2026-10-28.json](harvest/PASS2_RESUME_INVENTORY_2026-10-28.json).
- Each batch now contains **fresh**, canonical-derived follow-up queues:
  - `pass2_current_context_queue.jsonl`
  - `pass2_current_structure_queue.jsonl`
  - `pass2_current_classification_queue.jsonl`
  - `pass2_current_nonresult_queue.jsonl`
- Older dated `pass2_higher_thinking_remaining*.jsonl` and initial context diagnostics are retained for provenance but may contain candidates subsequently resolved. **Do not resume from those older queues** without checking the canonical Pass 2 status.
- Checkpoint workflow [Fresh resume queues and complete validation](https://github.com/Zengez/mathThm/actions/runs/40738980505) finished successfully.

## What requires further Pass 2

The **502 structure** cases have more intricate nested quantifier and list scopes, multiple hypotheses/conclusions with editorial prose, and some unconditional existence statements lacking a natural hypothesis side. The existing record contract presently requires a nonempty hypothesis field, so it is important **not** to invent an artificial premise merely to label unconditional theorems resolved.

The **1,099 context** cases include cross-chapter or section-level assumptions, older constructions described only as "above", and some references requiring actual local source interpretation rather than a regex substitution. Source-only follow-ups should identify the referenced definition/Situation/lemma precisely before promoting them.

The **three classification** cases all come from `trace.tex` and concern source-stated conjectures. In particular, one literally says a conjecture holds "modulo some unproven things"; none of these should be automatically treated as a fully verified theorem or rejected without an actual editorial judgment. They remain in the dedicated classification queue.

Suggested next effort: bounded direct mathematical reading of unresolved *statements and inherited assumptions* (not proofs), with individual source-context decisions and explicit defer reasons, and a design decision for unconditional results that correctly supports an empty hypothesis set. Do not silently turn a named conjecture into a confirmed theorem.

## Safety and publication

- No Pass 3 proof excerpts were opened or inspected; **0 Pass 3 records** in these three batches.
- No new theorem records were promoted into `data/theorems.json`.
- No mathematical-proof verification was claimed.
- Public mathThm theorem data were not modified by this continuation.
- Source reference was pinned at `a04446e57ec1fbc252a871afcec7752fb2807b14`.

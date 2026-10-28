# Pass 2 hard-case statement interpretation — October 28, 2026

**Scope:** ONLY the original two Stacks Project batches and their **827** `pass2_higher_thinking.jsonl` entries. The later third Pass 1 Stacks harvest is not part of these totals. This review did not open, read, or assess a proof, publish any new theorem, or perform deep outside mathematical research.

## Audited outcome

| Stage / outcome | First batch | Second batch | Combined |
| --- | ---: | ---: | ---: |
| Original hard-case Pass 2 queue | 295 | 532 | **827** |
| Explicit logical-form parsing (first review) | 206 | 427 | **633** |
| Additional targeted logical-form follow-up | 17 | 22 | **39** |
| Individually authored light editorial statement splits | 14 | 11 | **25** |
| **New Pass 2 statement splits** | **237** | **460** | **697** |
| **Still structurally difficult** | **58** | **72** | **130** |
| All Pass 2 resolved from original collections | 937 | 1,738 | **2,675** |
| Distinct candidates needing inherited source context | 105 | 212 | **317** |
| **All original Pass 2 work still open** | **163** | **284** | **447** |
| Pass 3 proofs checked | 0 | 0 | **0** |

This is **84.3%** recovery of the specific 827-item difficult queue (697/827). Overall 2,675 of 3,122 original candidates have source-statement hypothesis/conclusion structures (85.7%). Most are still *mechanical or light editorial interpretations*, not mathematical verification.

## Crucial user decision: equivalences

Retrieved the October 23 mathThm conversation decision: for `P iff Q iff R`, **every equivalent condition must be searchable in BOTH the hypotheses and conclusions fields**, while retaining a **single canonical displayed theorem**. Pass 2 `logical_form=equivalence` uses `equivalence_sides` and indexes each condition in both columns; `equivalence_with_additional_assertion` preserves non-equivalence consequences separately rather than accidentally upgrading them to an equivalent condition. The previously created requirement to handle equivalences as only a whole conclusion was corrected.

An audit of the current corpus found **195 theorem-level records with equivalence logical forms (76 first batch, 119 second); zero failed to index an equivalent condition in both search fields**. Also checked that no `resolved` record has an empty hypothesis or conclusion list. Embedded iff conditions within individual enumerated clauses are recorded as `equivalence_subcase` and indexed bidirectionally.

## Handling multi-part assertions

The first higher-thinking pass distinguished explicit equivalence lists, conjunctions of independently asserted clauses, diagrammatic statements, and initial setup followed by mathematical claims. The follow-up corrected per-case indexing for **295 source-enumeration records**: source clauses `If P then Q` now index `P` among hypotheses, `Q` among conclusions and keep the original clause under `structured_cases`; separate clauses are not silently merged into a purported single logical implication. A `P iff Q` list item indexes both directions. Some outcome records are still syntax-derived, and more semantic QA may be warranted.

A third, individually authored editorial tranche handled 25 compact but previously difficult cases, anchored by exact source candidate IDs and statement prefixes. Its decisions remain available in `harvest/pass2_manual_statement_review_2026-10-28.json`; the controlled application and final validation ran successfully.

## Durable records and continuation

The current **130** structurally open entries are persisted as:
- `harvest/batches/stacks-bulk-2026-10-28/pass2_higher_thinking_remaining_v3.jsonl` — 58 entries
- `harvest/batches/stacks-second-2026-10-28/pass2_higher_thinking_remaining_v3.jsonl` — 72 entries

The separate **317** `needs_context` cases were not part of this task and remain in `needs_more_investigation.jsonl`. They require retrieving inherited assumptions/notation, not proof research. Do not conflate their queue with the 130 structurally difficult cases. The source of truth for completed interpretations is `pass2.jsonl`, including `split_confidence`, `review_method`, `logical_form`, `equivalence_sides`, and `structured_cases`. Never assume a source-formulation split certifies mathematical truth or proof validity.

Successfully completed Github Actions:
- [Initial 633 structural interpretations](https://github.com/Zengez/mathThm/actions/runs/40727429255)
- [39 targeted follow-up interpretations and 295 per-case index repairs](https://github.com/Zengez/mathThm/actions/runs/40728140910)
- [25 source-anchored editorial statement interpretations](https://github.com/Zengez/mathThm/actions/runs/40728886377)

Each successful action ran the Python regression tests. Afterward, a direct read-only audit of both saved `pass2.jsonl` files verified exact totals, populated fields and equivalence indexing.

## Recommended next stage

For the 130 genuinely complex statements, review in small editor/model batches (roughly 10–20), prioritizing multi-enumeration premises, explicit alternative sufficient conditions, equivalences with additional corollaries, and diagrams with implicit scope. Avoid more broad regex-based acceptance because it risks false logical connections. Separately, address inherited context for the 317 context-blocked entries. Pass 3 remains on hold until authorized.

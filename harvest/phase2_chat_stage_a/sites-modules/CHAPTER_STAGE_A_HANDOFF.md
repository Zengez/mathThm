# `sites-modules.tex` — source-ordered Stage A chapter handoff

Pinned revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`. Branch: `work/phase2-stage-a-context-enrichment`.

All **45** complete physical sections checked (including candidate-free sections); **122** unique active candidates, **120** prepared for independent Stage B, **2** marked `further_work_needed`, no unprocessed active candidates.

There are **37** scoped context entries, **45** section checkpoints and 3 complete-section batches.

The source-section ledger contains definitions, named situations, notation, and scope guards, not copied standing assumptions from preceding theorems. Situation \ref{situation-quasi-compact-objects} is instantiated only where explicitly invoked in §30. The external Sites lemma's part-(4) premise at source lines 3532–3541 was expanded for the Hom/colimit candidate.

## Batch totals

| Batch | Sections | Active | Stage B-ready | Further work |

|---:|:---:|---:|---:|---:|

| 1 | 1–15 | 17 | 17 | 0 |

| 2 | 16–30 | 57 | 55 | 2 |

| 3 | 31–45 | 48 | 48 | 0 |

| **Total** | **1–45** | **122** | **120** | **2** |

## Unresolved source-specific issues

- §22, `lemma-localize-morphism-compare` (line 2775; harvest/phase2_chat_stage_a/sites-modules/batch_02_sections_16_30/RECONSTRUCTIONS.jsonl): The assertion identifies diagrams of two different localization lemmas only by external references. The site/topos comparison functors and arrow-level identifications must be explicitly matched against the pinned diagrams before claiming a standalone comparison.

- §22, `lemma-relocalize-morphism-ringed-topoi` (line 2807; harvest/phase2_chat_stage_a/sites-modules/batch_02_sections_16_30/RECONSTRUCTIONS.jsonl): Pinned source uses (f_c,f_c^sharp) in the first diagram but (f_s,f_s^sharp) subsequently, and the bottom-right structure sheaf in the final diagram is O'_{G'} instead of the apparent O'_G. The intended symbols/arrows require source adjudication; do not silently correct them.

## Scope and validation

Active IDs were reconciled against `harvest/active_candidate_ids.jsonl`, Pass 1 source locators and authoritative approved overlays. All original statements matched the pinned source exactly. No original source, proof, approved record, active pool, independent Stage B decision, or Phase 3 state was changed.

Checks here include JSON/JSONL construction, section coverage, uniqueness, source text exactness, decision counts, checkpoint continuity, and further-work registry reconciliation. This was **not** independent mathematical validation, proof screening, or a run of the repository's Python regression suite.

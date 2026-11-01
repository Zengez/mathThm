# Homology — Stage A source-first chapter handoff

**Pinned source:** [Stacks `homology.tex`](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/homology.tex) at `a04446e57ec1fbc252a871afcec7752fb2807b14`.
**Branch:** `work/phase2-stage-a-context-enrichment`. **Status:** Stage A pass complete; Stage B has not run for this chapter.

## Reconciled scope

- 32/32 physical source sections inspected in source order, including all candidate-free context-only sections (source lines 17–7946).
- 127 harvested statements, 119 active candidate IDs, 8 inactive IDs excluded, 0 previously approved candidates regenerated.
- 119 distinct active candidate reconstruction records: **109** `reconstruction_completed_awaiting_independent_stage_b_validation`, **10** `further_work_needed`.
- 71 source-anchored context/notation lookup events; 32 sequential section checkpoints.
- Zero proofs checked; zero independently Stage B-validated; zero Phase 3 promotions.

## Batch packets

| Packet | Sections | Active | Stage B-ready | Further work | Context events |
|---|---|---:|---:|---:|---:|
| [batch_01_sections_01_05](batch_01_sections_01_05/MANIFEST.json) | 1–5 | 27 | 26 | 1 | 13 |
| [batch_02_sections_06_12](batch_02_sections_06_12/MANIFEST.json) | 6–12 | 22 | 22 | 0 | 11 |
| [batch_03_sections_13_18](batch_03_sections_13_18/MANIFEST.json) | 13–18 | 16 | 16 | 0 | 18 |
| [batch_04_sections_19_24](batch_04_sections_19_24/MANIFEST.json) | 19–24 | 27 | 26 | 1 | 19 |
| [batch_05_sections_25_32](batch_05_sections_25_32/MANIFEST.json) | 25–32 | 27 | 19 | 8 | 10 |
| **Total** | **1–32** | **119** | **109** | **10** | **71** |

Each batch holds `RECONSTRUCTIONS.jsonl`, `CONTEXT_LEDGER.jsonl`, `SECTION_CHECKPOINTS.jsonl`, and `MANIFEST.json`. Batches with holds also have `FURTHER_WORK_NEEDED.jsonl`. Held IDs are registered in the global `harvest/phase2_chat_stage_a/FURTHER_WORK_NEEDED.jsonl`.

## Section disposition

| Section | Active | Ready | Further work |
|---|---:|---:|---:|
| §1: Introduction | 0 | 0 | 0 |
| §2: Basic notions | 0 | 0 | 0 |
| §3: Preadditive and additive categories | 10 | 9 | 1 |
| §4: Karoubian categories | 2 | 2 | 0 |
| §5: Abelian categories | 15 | 15 | 0 |
| §6: Extensions | 2 | 2 | 0 |
| §7: Additive functors | 4 | 4 | 0 |
| §8: Localization | 4 | 4 | 0 |
| §9: Jordan-H"older | 4 | 4 | 0 |
| §10: Serre subcategories | 5 | 5 | 0 |
| §11: K-groups | 1 | 1 | 0 |
| §12: Cohomological delta-functors | 2 | 2 | 0 |
| §13: Complexes | 8 | 8 | 0 |
| §14: Homotopy and the shift functor | 5 | 5 | 0 |
| §15: Truncation of complexes | 0 | 0 | 0 |
| §16: Graded objects | 1 | 1 | 0 |
| §17: Additive monoidal categories | 2 | 2 | 0 |
| §18: Double complexes and associated total complexes | 0 | 0 | 0 |
| §19: Filtrations | 13 | 13 | 0 |
| §20: Spectral sequences | 0 | 0 | 0 |
| §21: Spectral sequences: exact couples | 2 | 1 | 1 |
| §22: Spectral sequences: differential objects | 2 | 2 | 0 |
| §23: Spectral sequences: filtered differential objects | 3 | 3 | 0 |
| §24: Spectral sequences: filtered complexes | 7 | 7 | 0 |
| §25: Spectral sequences: double complexes | 4 | 1 | 3 |
| §26: Double complexes of abelian groups | 4 | 2 | 2 |
| §27: Injectives | 2 | 2 | 0 |
| §28: Projectives | 2 | 2 | 0 |
| §29: Injectives and adjoint functors | 4 | 4 | 0 |
| §30: Essentially constant systems | 3 | 2 | 1 |
| §31: Inverse systems | 7 | 5 | 2 |
| §32: Exactness of products | 1 | 1 | 0 |

## Exact further-work worklist

1. **§3, [lemma-idempotent-splitting](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/homology.tex#L421) (L421)** — Expand and reconcile the four conditional kernel/cokernel splittings of the idempotent's complementary projectors. Packet: `harvest/phase2_chat_stage_a/homology/batch_01_sections_01_05/RECONSTRUCTIONS.jsonl`.
2. **§21, [lemma-derived-exact-couple](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/homology.tex#L5314) (L5314)** — Replace the formal `g∘α⁻¹` symbol with an explicit well-defined morphism of the derived exact couple. Packet: `harvest/phase2_chat_stage_a/homology/batch_04_sections_19_24/RECONSTRUCTIONS.jsonl`.
3. **§25, [lemma-ss-double-complex](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/homology.tex#L6607) (L6607)** — Verify existence of totalization and both filtrations for unrestricted double complexes in an arbitrary abelian category. Packet: `harvest/phase2_chat_stage_a/homology/batch_05_sections_25_32/RECONSTRUCTIONS.jsonl`.
4. **§25, [lemma-double-complex-gives-resolution](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/homology.tex#L6698) (L6698)** — The unspecific asserted second-variable variant needs complete hypotheses and maps; main claim is recorded. Packet: `harvest/phase2_chat_stage_a/homology/batch_05_sections_25_32/RECONSTRUCTIONS.jsonl`.
5. **§25, [lemma-homotopy-complex-complexes](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/homology.tex#L6745) (L6745)** — Verify existence and intended convention for potentially unbounded total complexes without added coproduct hypotheses. Packet: `harvest/phase2_chat_stage_a/homology/batch_05_sections_25_32/RECONSTRUCTIONS.jsonl`.
6. **§26, [lemma-good-right-resolution-gives-qis](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/homology.tex#L6927) (L6927)** — Spell out the proof-local product-totalization objects and signed differential, without confusing them with direct-sum totalization. Packet: `harvest/phase2_chat_stage_a/homology/batch_05_sections_25_32/RECONSTRUCTIONS.jsonl`.
7. **§26, [lemma-resolution-gives-qis](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/homology.tex#L7016) (L7016)** — Spell out the proof-local product-totalization objects and signed differential, and confirm the augmentation map. Packet: `harvest/phase2_chat_stage_a/homology/batch_05_sections_25_32/RECONSTRUCTIONS.jsonl`.
8. **§30, [lemma-essentially-constant-into-karoubian](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/homology.tex#L7466) (L7466)** — Reconcile the external definition of essentially constant with the cofinal/initial splitting and object quantifiers. Packet: `harvest/phase2_chat_stage_a/homology/batch_05_sections_25_32/RECONSTRUCTIONS.jsonl`.
9. **§31, [lemma-inverse-systems-abelian](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/homology.tex#L7615) (L7615)** — Resolve the undefined `N_i` in the componentwise exactness criterion (source's sequence ends in `M_i`). Packet: `harvest/phase2_chat_stage_a/homology/batch_05_sections_25_32/RECONSTRUCTIONS.jsonl`.
10. **§31, [lemma-essentially-constant](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/homology.tex#L7732) (L7732)** — Import and reconcile the pinned Categories definition of essentially constant and the eventual canonical direct-sum decomposition. Packet: `harvest/phase2_chat_stage_a/homology/batch_05_sections_25_32/RECONSTRUCTIONS.jsonl`.

## Context and correctness rules

Read source in chronological section order. Definitions and section remarks are lookup leads, not blanket ambient hypotheses. In particular, the two natural double-complex filtrations were introduced as construction data, and inverse-system index direction and the Mittag–Leffler stabilization condition were kept local to their actual use. Prior lemma-specific objects and hypotheses are discharged at environment boundaries. Inactive candidates are not recreated as Stage A drafts.
Stage A reconstructed the source assertions and expanded internal references where support was available, but did **not** perform proof checking, independent semantic validation or Stage B decisions. Any `further_work_needed` reconstruction is only a partial working draft and is **not** available for Stage B until resolved.

## Codex Stage B selection

Use the five batch `RECONSTRUCTIONS.jsonl` packets as exact input sources, selecting only records with `decision == "reconstruction_completed_awaiting_independent_stage_b_validation"`; the selected count is **109**. Use exact `candidate_id` identity to prevent reprocessing, retain source attribution and the pinned revision, and use surrounding context ledgers and checkpoints only as supporting references. Do not process the ten `further_work_needed` records as accepted standalone inputs. Perform independent mathematical/proof validation and only then assign Stage B decisions; do not interpret this Stage A readiness as Phase 3 approval. Avoid full-corpus preloading and repeated global skip scans; work by packet/section.

## Structural verification

Checks completed: each of 119 active source IDs appears exactly once; source statements and line labels match Pass 1 and the pinned Stacks source; five manifests sum to 119, with 109 ready and ten holds; 32 contiguous section checkpoints; each hold is in the global registry exactly once; all ready records have nonempty hypotheses/conclusions and no unresolved LaTeX `\ref{...}`; no `proof_reviewed`, Stage B-validated or Phase 3 flags were set. These are file/identity/structural checks, **not** a run of the repository's regression suite or an independent Stage B mathematical review.

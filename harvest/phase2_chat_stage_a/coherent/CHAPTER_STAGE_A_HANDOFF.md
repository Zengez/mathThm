# Coherent chapter — Stage A source-first Codex handoff

- Source: pinned `coherent.tex` at `a04446e57ec1fbc252a871afcec7752fb2807b14` (Cohomology of Schemes; 28 sections, source lines 17–8138).
- Working branch: `work/phase2-stage-a-context-enrichment`.
- **121 active canonical** theorem candidates, **30 already-authoritatively-approved excluded**, **91 newly prepared by Chat**, **89 awaiting independent Stage B**, **2 further-work holds**. Six other pinned theorem-like environments are outside the active registry and were not added.
- Four batch commits: `cf2ceb95f0411be9a3814388cedf2eca543d8f48`, `c9f1ebba49713fc28a9b2e7b71a48aa1e9acf550`, `d260c23710d4b3ff83110aaff4b5081ad5975d9d`, `289adb12b03a89ef6ec822ad22046b4510bc774c`.

## Batch population

| Source sections | New candidates | Stage A ready | Further work | Previous approvals excluded |
|---|---:|---:|---:|---:|
| §§1–8 | 23 | 22 | 1 | 0 |
| §§9–16 | 29 | 28 | 1 | 12 |
| §§17–22 | 7 | 7 | 0 | 18 |
| §§23–28 | 32 | 32 | 0 | 0 |
| **Total** | **91** | **89** | **2** | **30** |

Each `batch_NN_sections_MM_NN` directory contains `RECONSTRUCTIONS.jsonl`, `CONTEXT_LEDGER.jsonl`, `SECTION_CHECKPOINTS.jsonl`, and `MANIFEST.json`. All 28 sections have checkpoints, including those containing only already-approved records or definitions/context. There are no duplicate newly prepared candidate IDs. The source pinned revision and label matching were checked for every new candidate. Each record has hypotheses, conclusions, original source statement, and a concrete readiness decision.

## Source-order context and corrections

- §2 affine-diagonal and §9 coherent-sheaf characterization: all equivalence clauses belong in conclusions rather than premises.
- §§5 and 7 base-change: reconstruct the cartesian square, quasi-coherence and affine-diagonal assumptions, and preserve the independent affine-base-change guard.
- §§4, 9, 10, 17, 21, and 26: preserve conditional guards, independent listed assertions, equivalences, and correct quantifier scope.
- §12 devissage: preserve nested existential conditions as hypotheses of the property criteria, rather than extracting them as consequences.
- §20 formal functions: preserve the section's ideal-power notation, common `c` witnessing multiple clauses, and independent inverse-system/Mittag-Leffler results.
- §§23–27: preserve the definition of `Coh(X,I)` for coherent formal systems, the completion functor `F ↦ (F/I^nF)`, and proper-support subcategories as named setup, never previous lemma-local assumptions.
- §28: distinguish compatible cartesian diagrams, properness and ampleness hypotheses from the simultaneous algebraization conclusion.

## Precisely localized holds

1. `lemma-cohomology-projective-space-over-base`, [coherent.tex L2004](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/coherent.tex#L2004), `candidate.stacks.4931b7859f6b6dd084c3a3ec`: For n=0, the source piecewise formula has overlapping q=0 and q=n branches; the correct case priority and degree bounds are not explicit in a standalone split. Resolve n=0 against preceding coherent.tex projective-space degree conventions without inventing an extra case.

1. `lemma-hom-into-depth`, [coherent.tex L2836](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/coherent.tex#L2836), `candidate.stacks.732b1c201e494c888db32925`: The second depth assertion uses Hom_{O_X}(F,G)_x while the first uses SheafHom; its local O_{X,x}-module interpretation requires source-specific confirmation. Check the distinction against the depth definition and surrounding Stacks Hom notation before normalizing the stand-alone statement.

## Codex Stage B selection

Read the four batch files `RECONSTRUCTIONS.jsonl` in source order. Select **only** records with `decision == "reconstruction_completed_awaiting_independent_stage_b_validation"` and an empty `stage_a_remaining_work`. The 30 approved candidates have no newly generated records and must not be reconsidered; the two holds are recorded in the central `FURTHER_WORK_NEEDED.jsonl` with batch paths. Verify exact semantic equivalence independently against the pinned original and preserved context. Source proof bodies were not screened or reviewed; no Phase 3 eligibility or publication was granted by these overlays. This run did not modify Pass 1/Pass 2, approved overlays, or the production theorem catalog.

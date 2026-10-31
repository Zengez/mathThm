# `sites-cohomology.tex` — Stage A chapter handoff

Pinned Stacks revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`. Branch: `work/phase2-stage-a-context-enrichment`.

**Complete disposition:** 53/53 physical sections scanned in source order (45 with active candidates); 216/216 active candidates covered exactly once; **211 prepared for independent Codex Stage B**, **5 flagged `further_work_needed`**, 0 unprocessed active candidates.

Fifteen batch directories each contain `MANIFEST.json`, `RECONSTRUCTIONS.jsonl`, `CONTEXT_LEDGER.jsonl`, and `SECTION_CHECKPOINTS.jsonl`. The accumulated 82 ledger entries distinguish definitions/notation and source-local situations; theorem-local hypotheses do not flow into later sections. All 53 section checkpoints reconcile without gaps. Original source statements, pinned reference leads and explicit hypothesis/conclusion reconstructions are preserved in per-candidate records.

## Codex selection rule

**Process only** records whose `decision` is `reconstruction_completed_awaiting_independent_stage_b_validation` (211 records). These have **not** been independently Stage B validated. Do **not** assume they have been proof-screened or admitted to Phase 3. Do not process `further_work_needed` records as already-ready; handle those five separately after adjudicating the specific issue. If independent review finds further omissions, lower the readiness flag rather than silently repairing underlying source assertions.

## Five outstanding source/reconstruction problems

1. **§33, `lemma-base-change-cup-product` (source line 8528).** Source bottom-left vertex malformed: unbalanced parentheses and apparent wrong tensor coefficient ring; verify corrected diagram and arrow orientations. Record: `harvest/phase2_chat_stage_a/sites-cohomology/batch_10_sections_31_33/RECONSTRUCTIONS.jsonl`.
2. **§38, `lemma-compute-pi-shriek` (source line 9959).** The presheaf transition/restriction maps are deferred to a proof and must be reconstructed/coherence-checked. Record: `harvest/phase2_chat_stage_a/sites-cohomology/batch_12_sections_37_42/RECONSTRUCTIONS.jsonl`.
3. **§40, `lemma-compute-left-derived-g-shriek` (source line 10677).** The categories I_U, coefficients F'_U and restriction maps are only defined in a proof and must be reconstructed. Record: `harvest/phase2_chat_stage_a/sites-cohomology/batch_12_sections_37_42/RECONSTRUCTIONS.jsonl`.
4. **§43, `lemma-QC-hom-out-of-plus-topology` (source line 11677).** Source equates a Hom set with an RHom complex; determine intended cohomological degree/target. Record: `harvest/phase2_chat_stage_a/sites-cohomology/batch_13_sections_43_45/RECONSTRUCTIONS.jsonl`.
5. **§45, `lemma-pseudo-coherent-pullback` (source line 12109).** Source declares E∈D(O_C) while Lf^* requires a derived object over O_D. Record: `harvest/phase2_chat_stage_a/sites-cohomology/batch_13_sections_43_45/RECONSTRUCTIONS.jsonl`.

All five are registered once in `harvest/phase2_chat_stage_a/FURTHER_WORK_NEEDED.jsonl`.

## Batch summary

| Batch | Physical sections | Active candidates | Ready for Stage B | Further work |
|---:|:---:|---:|---:|---:|
| 1 | 1–8 | 10 | 10 | 0 |
| 2 | 9–10 | 15 | 15 | 0 |
| 3 | 11–15 | 18 | 18 | 0 |
| 4 | 16–17 | 18 | 18 | 0 |
| 5 | 18–20 | 22 | 22 | 0 |
| 6 | 21–23 | 16 | 16 | 0 |
| 7 | 24–25 | 5 | 5 | 0 |
| 8 | 26–29 | 8 | 8 | 0 |
| 9 | 30–30 | 8 | 8 | 0 |
| 10 | 31–33 | 11 | 10 | 1 |
| 11 | 34–36 | 16 | 16 | 0 |
| 12 | 37–42 | 12 | 10 | 2 |
| 13 | 43–45 | 18 | 16 | 2 |
| 14 | 46–48 | 22 | 22 | 0 |
| 15 | 49–53 | 17 | 17 | 0 |
| **Total** | **1–53** | **216** | **211** | **5** |

## Validation and cautions

- Manifest candidate ID set matches the pinned-source active candidate registry: 216 unique identifiers, no omissions or duplicates.
- Source section checkpoints cover lines 17–14428 continuously; no carried standing hypotheses or lost definitions/guards.
- Local source anomalies (including the five pending issues) were not silently normalized into unsupported source assertions.
- The `lemma-cohomology-bigger-site` candidate intentionally replaces a cross-reference with the pinned external premise list; its original verbatim source is retained in `original_source_statement_tex`, which explains a permitted raw-text mismatch.
- Independent Stage B validation, proof evaluation, publication, and Phase 3 promotion were **not** performed by this run.

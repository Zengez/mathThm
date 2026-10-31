# Stage B calibration checkpoint — 2026-10-31

Working checkout: `/home/jason/Projects/mathThm/.harvest_runs/stage-b-calibration-20261031` on `codex/phase2-validation`.

Fixed Stage A snapshot: `12ecd17763643ef1dcc4607042450d8555a5446d`.
Pinned Stacks: `a04446e57ec1fbc252a871afcec7752fb2807b14` via ignored upstream symlink.

`SELECTION.json` is the fixed assignment: 50 sections, 193 eligible candidates, out of 288 eligible sections at startup. Exclude Topologies, Descent, all prior completed IDs, and all unready records. Do not refresh enrichment branch. Imported input blobs match pinned Git blob hashes. Existing historical 655 and recovered materialized 27 approvals are preserved (baseline 682); no calibration approvals have been materialized at this checkpoint.

First calibration group: ordinals 1–8, 31 eligible candidates at more-morphisms.tex:4438–6154. `initial_08/FORMULATIONS.jsonl` and `SECTION_CHECKPOINTS.json` record the correction pass, saved at complete-section boundaries. Independent validation must be checked in its own artifact; correction completion alone is not approval. At checkpoint creation there are 13 formulations across ordinals 1–4 and no saved independent decisions. Active workers may extend these files, so inspect their latest content before resuming; never overwrite completed records.

Next steps: finish correction and independent source-first validation of first eight, run focused identity/provenance/digest/workflow checks, and checkpoint before processing selected ordinals 9–50. Use existing materialization with a current-run-only REVIEW_BATCHES manifest and explicit output to avoid duplicating historical approvals. Never inspect proofs. Preserve mathematical holds. Do not claim mixed sections fully reviewed while unready candidates remain. Stop after selected 50 for external audit.

Recovered checkout `.harvest_runs/stage-b-validation-20261030` remains untouched. Its 78 independent Topologies decisions and 129 Descent formulations remain excluded. Only already-materialized 27 overlays and their provenance were copied into this isolated checkout, without fresh review.

Local Git is writable in this isolated checkout; original root .git is read-only. Do not repeatedly retry blocked push/network operations. Full tests deferred per user; run focused calibration checks only. No focused checks have run yet at checkpoint creation. No reliable per-run token/credit telemetry is available.

## Initial gate completed

All initial31 formulations and independent approvals saved; nine mathematical corrections, no holds. Existing authoritative/workflow tests:13 passed. Focused current-run checks passed exact eligible identity, disjoint historical IDs, snapshot blob provenance, independent reviewer, proof exclusion, exact formulation digest, and mutation rejection. Existing materialization succeeded:31 new approvals, union713=655 historical+27 recovered+31 new. Materializer corrected to honor per-batch review_date (historical default retained).

Authorized continuation ONLY ordinals9–50: bulk_09_22 (55 IDs), bulk_23_36 (65 IDs), bulk_37_50 (42 IDs). Correction and independent source-first roles dispatched; inspect section checkpoints/current files on resume before doing any work. Final target remains50 sections/193 eligible candidates, never expand. For final materialization add completed bulk pairs to this run's REVIEW_BATCHES.json; output same APPROVED_OVERLAYS.jsonl, preserving initial31. Full suite remains deferred.

## Through selected ordinal22

86 new independent approvals now materialized (initial31+bulk55); authoritative union768. Sections9–22 completed; three further structured corrections documented. Remaining ordinals23–50 in progress.

Proof-exposure incident: ordinal30, flat.tex2136–2341 has informal proof-bearing remark2291–2327 outside proof environments. Both reviewers transparently reported exposure before any ordinal30 verdict. Its three selected IDs must remain distinct processing holds, not approvals/no-proof attestations. Correction agent will save separate HELD_PROOF_EXPOSURE records; final exact coverage must include those IDs without weakening existing proof exclusion gates. Later source displays mask proof-bearing remarks explicitly. Preserve incident notes and do not repeat exposed reviews as clean passes.

## Through ordinal36

148 new approvals materialized, three explicit proof-exposure processing holds. The independent validator required finite-strata index quantification correction and re-reviewed the exact final row. Only selected ordinals37–50 (42 IDs) remain. Separate counterpart incident records are in bulk_23_36; never materialize them.

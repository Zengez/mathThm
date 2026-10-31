# Stage B calibration checkpoint — 2026-10-31

Working checkout: `/home/jason/Projects/mathThm/.harvest_runs/stage-b-calibration-20261031` on `codex/phase2-validation`.

Fixed Stage A snapshot: `12ecd17763643ef1dcc4607042450d8555a5446d`.
Pinned Stacks: `a04446e57ec1fbc252a871afcec7752fb2807b14` via ignored upstream symlink.

`SELECTION.json` is the fixed assignment: 50 sections, 193 eligible candidates, out of 288 eligible sections at startup. Exclude Topologies, Descent, all prior completed IDs, and all unready records. Do not refresh enrichment branch. Imported input blobs match pinned Git blob hashes. Existing historical 655 and recovered materialized 27 approvals are preserved (baseline 682); no calibration approvals have been materialized at this checkpoint.

First calibration group: ordinals 1–8, 31 eligible candidates at more-morphisms.tex:4438–6154. `initial_08/FORMULATIONS.jsonl` and `SECTION_CHECKPOINTS.json` record the correction pass, saved at complete-section boundaries. Independent validation must be checked in its own artifact; correction completion alone is not approval. At checkpoint creation there are 13 formulations across ordinals 1–4 and no saved independent decisions. Active workers may extend these files, so inspect their latest content before resuming; never overwrite completed records.

Next steps: finish correction and independent source-first validation of first eight, run focused identity/provenance/digest/workflow checks, and checkpoint before processing selected ordinals 9–50. Use existing materialization with a current-run-only REVIEW_BATCHES manifest and explicit output to avoid duplicating historical approvals. Never inspect proofs. Preserve mathematical holds. Do not claim mixed sections fully reviewed while unready candidates remain. Stop after selected 50 for external audit.

Recovered checkout `.harvest_runs/stage-b-validation-20261030` remains untouched. Its 78 independent Topologies decisions and 129 Descent formulations remain excluded. Only already-materialized 27 overlays and their provenance were copied into this isolated checkout, without fresh review.

Local Git is writable in this isolated checkout; original root .git is read-only. Do not repeatedly retry blocked push/network operations. Full tests deferred per user; run focused calibration checks only. No focused checks have run yet at checkpoint creation. No reliable per-run token/credit telemetry is available.

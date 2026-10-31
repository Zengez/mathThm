# A0 calibration result — 2026-10-31

**Branch:** `work/phase2-stage-a-context-enrichment`  
**Source:** pinned Stacks `flat.tex`, revision `a04446e57ec1fbc252a871afcec7752fb2807b14`, §§1–42 (source lines 18–13451).

## Observed output

| Metric | Value |
|---|---:|
| Physical full sections traversed | 42 |
| Candidate-bearing full sections | **40** |
| Source-derived candidate overlays | **231** |
| Unique candidate IDs | **231** |
| A0 inherited-context blockers | **10** |
| No safe low-inference rewrite made | **221** |
| Actual rewritten standalone statements | **0** |
| Candidate records containing reference lookups | **87** |
| Source-anchored ledger entries | **28** |
| Section checkpoints | **42** |
| Stage A / Codex readiness mutations | **0** |
| Proofs mathematically examined | **0** |

Four batches: `flat/batch_01_sections_01_10`, `flat/batch_02_sections_11_20`, `flat/batch_03_sections_21_31`, `flat/batch_04_sections_32_42`. Each contains a manifest, candidate overlays, ledger entries, post-section checkpoints and a report. JSON and JSONL parse checks, row-count reconciliation, unique candidate IDs and no-readiness-leakage checks passed across all four batches. This was *not* a complete mathematical audit or full regression suite.

## Interpretation and limits

This **does not yet demonstrate the hoped-for Stage A time saving**. The trial successfully gathered source-anchored references and section checkpoints, but did not actually insert contextual prerequisites into any candidate statement. `a0_no_changes_needed` is merely an honest statement that no mechanically safe rewrite was made, **not** a claim that those 221 candidates are standalone or easy for A1. There remain both false-negative contextual dependencies and unverified scope judgments to audit. The status should not be used as a positive A1 difficulty prediction until independently evaluated.

In the first ten sections, six explicit inherited-setup cases (e.g. `lemma-devissage-finite-presentation`, `lemma-devissage-flat`, `lemma-homothety-universally-injective`) were identified; ten such holds across the full window. A1 must reconstruct the referenced assumptions/objects, and check additional candidates that this lightweight pattern matcher did not flag.

**Two promised selection/integrity checks were not completed:** (1) the arbitrary ~200 candidate-bearing-section collision buffer from the concurrent A1 frontier was not measured (nor was an exact offset required), and (2) candidate membership in the full 9,675-ID active registry and later Codex-approved IDs beyond the inspected original chapter coverage could not be exhaustively reconciled through the available connector. The generated IDs use the Pass 1 pinned source/label fingerprint method, but this alone does not authorize active-pool membership. Treat the entire pilot as **provisional A0-only overlays** until those crosschecks are made.

**Thinking-level clarification (confirmed by the user):** the original calibration **was run with Medium thinking**. The execution interface did not record a controlled Medium-versus-High A1 comparison, so no speedup or cost-savings measurement is established. The separate A0 v2 audit added source work packets after the Medium run.

## Recommended adjustment before another A0 run

1. Add **verified direct-source substitutions** for a narrow, high-confidence subset of inherited contexts; retain a transformation-by-transformation provenance trail. Merely annotating an explicit lemma reference may save lookup time but not reconstruction time.
2. Audit 10–15 source contexts in A1 (including apparently self-contained ones) to establish the actual missing-context rate and error rate.
3. Resolve the official source-order offset/current frontier and full active/approval-ID exclusions before running concurrent A0 and A1 at scale.
4. Measure A1 review effort with and without the reference ledger; scale only if the benefit is real.

**No authoritative Stage A, Stage B, Pass 3, or public-catalog records were modified.**

## Subsequent audit, not part of the original Medium run

The later [A0 v2 review](REVIEW_AND_V2_SPEC_2026-10-31.md) found many missed explicit inherited-context references and produced separate `A0_WORKPACKETS_V2.jsonl` per calibration batch, plus `flat/CONTEXT_EVENTS_V2.jsonl` to index omitted named Situations. It preserves the original candidate overlays and the original Medium results for comparison. The retrofitted v2 source packets do **not** retrospectively prove the Medium run was successful or completed any standalone mathematical validation.

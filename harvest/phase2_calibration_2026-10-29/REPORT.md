# Phase 2 mathematical review checkpoint — October 29, 2026

This is an incomplete corpus-wide task. It records actual individual mathematical statement reviews, not proof verification. Pinned Stacks revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`.

## Results

| State | Candidates |
|---|---:|
| Active canonical population | 9,675 |
| Fully Phase 2 validated and Phase 3 eligible | 144 |
| Awaiting mathematical validation | 1,106 |
| Contextual reconstruction required | 370 |
| Earlier pilot reconstructions awaiting reconciliation | 30 |
| Not yet standalone reconstructed | 8,025 |
| Uncorrected historical eight reconstruction defects | 0 |

The five disjoint working states sum to 9,675. Eight provisional duplicate canonical groups remain blocked; these are a secondary flag, not eight additional candidates.

**New approvals: 76** (68 calibration approvals plus eight corrected historical defects). The original 68 approval histories are preserved and their authoritative formulations materialized, including the four previously separated corrections.

The initial calibration covered 69 candidates in three full sections: algebra.tex 6649–7433 (14), algebra.tex 7434–7970 (22), and descent.tex 5459–6305 (33). Independent source-first reviewers approved 68 and held one. Thirty-eight preliminary reconstructions required corrections (6 algebra, 32 descent). This is actual statement/context review, not an empirical guarantee of mathematical correctness.

A further 46 Stage A reconstructions in four complete algebra sections (7971–9513), including 17 corrections, are saved in `algebra_next/`; independent Stage B review is still required. Four previously held reconstructions became Stage A drafts; they are included in the 1,106 awaiting review, never counted as approved.

## Mathematical findings

- Descent drafts had malformed hypothesis fields or treated the property being descended as a premise. Expanded the actual fpqc-locality definition as a quantified base-change equivalence. Preserved quasi-compact AND dominant, both quasi-finite variants, unramified versus G-unramified, and fixed-degree finite locally free assertions.
- Jacobson reconstructions needed joint existential witnesses and the separately guarded reverse assertion. Preserved strict cardinal bounds and avoided inserting Noetherian assumptions.
- Independent validation caught unsupported interpretation of "integrally closed" for arbitrary maps in `lemma-finite-product-integral-closure`. The source's preceding definition is for inclusions, but the lemma uses maps. The invented image interpretation was removed; this remains a precise context hold, not an approval. Do not silently add injectivity.
- All eight historical defects were corrected and independently reviewed: graded Serre quotient categories and nonstandard irrelevant modules; the generator-degree lcm; separate graded-module/sheaf twists; QCQS as antecedent; degree-zero localization and X_s; the omitted universal-base-change clause; alternative sufficient conditions; and higher-direct-image coefficient/pullback conventions.

## Downstream and integrity

`harvest/PHASE2_AUTHORITATIVE_REGISTRY.json` explicitly names authoritative overlay files. The pipeline consumes the approved unified statement, hypotheses, conclusions and logical metadata, and binds future proof decisions to that formulation's digest. Missing or stale approval fails closed. Original raw statements and historical Pass 1/2 records remain untouched. No real campaign Phase 3 packets, proof screening, publication, or production changes were executed.

Independent review hashes bind exact formulations including logical metadata. Materialization initially stopped on stale hashes after metadata changes; the independent reviewer rechecked the final metadata and updated the attestations. This failure correctly prevented stale formulations being promoted. It was an integration issue, not loss of candidate data.

One geometry source retrieval accidentally displayed trailing proof text before filtering was corrected. No proof assessment or screening was performed, no mathematical approval relied on it, and the incident is recorded in the geometry section checkpoint. Subsequent source displays excluded proof environments.

The initial 139-test baseline grew to 152 Python regression tests, all passing at closeout. Checks cover historical corrected formulations, source/draft provenance, stale downstream decisions, exact independent review binding, population reconciliation, and repair regression examples. Synthetic test fixtures exercise future pipeline stages; they are not actual corpus proof reviews.

No defensible wall-clock mathematical throughput measurement was captured in the interrupted run; do not extrapolate a candidates/hour rate. Calibration demonstrates 69 substantive reviews with independent checks, not an established maximum batch size.

## Resume

1. Read `STATUS.json`, `REVIEW_BATCHES.json`, this report, and the current top of `WORK_CHECKPOINT.md`.
2. Independently review all 46 records in `algebra_next/RECONSTRUCTIONS.jsonl` against pinned source statements/context (mask proof bodies before displaying). Record candidate-specific decisions and precise holds; use a different reviewer from the reconstructor.
3. Hash the exact reviewed record with `scripts.phase2_authoritative.content_digest`. Re-review any formulation changed after validation; do not merely refresh hashes.
4. Append finalized review pairs to `REVIEW_BATCHES.json`, remove the corresponding pending batch entry, and retain all previous batches/history. A new batch must not overlap prior reviews. Do not edit historical source records.
5. Run `python3 -m scripts.phase2_review_workflow materialize` and `python3 -m scripts.phase2_review_workflow status`. Materialization checks explicit human/model approvals; it does not decide mathematical equivalence.
6. Run `python3 -m unittest discover -s tests -q`. Snapshot counts in the calibration tests should be scoped/updated deliberately when adding new batches.
7. Continue pending draft-ready candidates, full source sections, separate reconstruction and independent validation. Keep the eight provisional duplicate gates blocked until individually adjudicated. No Phase 3 or publication is authorized by this task.

Branch: `codex/phase2-validation`. The local closeout commit contains these artifacts; no push was performed.

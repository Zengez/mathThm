# Phase 3 frozen candidate ID audit — 2026-11-02

**Result: PASS.** This records the complete independent ID/provenance/metadata audit of the four reconciled worker lanes, after correcting malformed SHA-256 metadata in the integrated copy of 31 proposal files. The original four worker branches remain unchanged.

- Audit: [successful GitHub Actions run](https://github.com/Zengez/mathThm/actions/runs/41577665191).
- Audited reconciled-and-corrected commit: `cd2f6d1e45c6a41b90cb15d80580f637bf368de5`.
- Frozen initial Stage B / Phase 3 allocation base: `c57a162275ef35a7fe61e87f709627fd98ede4de`.
- Pinned Stacks source revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`.
- Reproducible validation: `python scripts/phase3_id_audit.py --report /tmp/phase3-id-audit.json`.

## Frozen ID accounting

| Worker | Whole sections | Positive IDs | Materialization proposals | Provisional proof reviews | Held excluded |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 320 | 971 | 971 | 971 | 190 |
| 2 | 277 | 939 | 939 | 939 | 219 |
| 3 | 323 | 992 | 992 | 992 | 166 |
| 4 | 324 | 964 | 964 | 964 | 193 |
| **Total** | **1,244** | **3,866** | **3,866** | **3,866** | **768** |

Every positive ID in the frozen Stage B input has exactly one materialization proposal and one provisional proof review. No missing, extra, duplicate, cross-worker-colliding, or held-leaked IDs were detected. All frozen source-section Git blob SHAs match, and original source identities and the reviewed final `statement`, `hypotheses`, `conclusions`, and `logical_form` are unchanged. No provisional record falsely asserts authoritative approval, official Phase 3 admission, or publication.

## Provisional proof screens

| Worker | Plausible | Questionable | Deferred |
| --- | ---: | ---: | ---: |
| 1 | 827 | 134 | 10 |
| 2 | 679 | 166 | 94 |
| 3 | 812 | 180 | 0 |
| 4 | 743 | 221 | 0 |
| **Total** | **3,061** | **701** | **104** |

Outcomes are **provisional**, based on cursory proof-screening evidence. This audit verifies the metadata and the reviewed-content linkage, **not** proof correctness. A favorable preliminary screen is not authoritative Phase 2 approval.

## Correction performed

The initial full ID audit exposed 117 malformed `source_statement_sha256` metadata fields: 10 in worker 2 and 107 in worker 3. Each was recomputed deterministically from the *exact* unchanged frozen Stage B `original_source_statement_tex` after checking that the worker's reviewed statement and source identity matched the frozen record. Exactly 31 worker proposal JSONL files were modified in the **integration branch only**, with no candidate ID, statement, hypothesis, conclusion, logical form, proof review, or publication flag changed. A second full audit completed successfully with zero reported issues.

Forty-seven records have empty hypothesis arrays; these can represent unconditional mathematical statements and are not treated as an integrity failure.

## Scope and remaining publication gates

This audit does **not** independently reopen every original upstream proof, certify mathematical truth, or register Phase 2 authoritative approval. Prior to public catalog promotion:

1. Independently approve and register the exact final Phase 2 formulations and their content digests under the authoritative registry, with duplicate review.
2. Match provisional proof decisions against the registered final content and import only genuinely completed and adequately supported plausible proof screens into official Pass 3; recheck any stale or incomplete evidence.
3. Keep the 701 questionable and 104 deferred proof screens and the original 768 Stage B holds out of accepted publication until separately resolved.
4. Validate source attribution/licensing, canonical IDs, duplicates, and accepted schema, generate a reviewed theorem catalog, test the website, and merge the approved publication output to `main`.

The core ID/provenance reconciliation gate is complete. This is not a mathematical-proof-verification or publication approval.

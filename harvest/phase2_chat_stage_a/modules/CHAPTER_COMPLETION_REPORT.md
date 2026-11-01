# Modules chapter — source-ordered Stage A preparation

Pinned source: [Stacks Project `modules.tex`](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/modules.tex), revision `a04446e57ec1fbc252a871afcec7752fb2807b14`. Isolated review branch: `work/modules-source-prepass-20261101`.

## Coverage

| Measure | Count |
|---|---:|
| Physical source sections traversed and checkpointed | **31 / 31** |
| Candidate-bearing sections | **27** |
| Context-only sections | **4** |
| Harvested theorem-like source records | **119** |
| Canonical active candidate IDs | **110** |
| Excluded/nonactive candidates | **9** |
| Overlap with authoritative approvals | **0** |
| Active Stage A candidate dispositions | **110 / 110** |
| **Standalone-prepared for independent Codex Stage B** | **108** |
| **Further work needed** | **2** |
| Unprocessed active Stage A candidates | **0** |
| Independent Stage B validations / Phase 3 approvals | **0 / 0** |

## Three source-ordered batches

| Sections | Active | Prepared | Further work | Artifact directory |
|---|---:|---:|---:|---|
| §§1–10 | 26 | 26 | 0 | `batch_01_sections_01_10/` |
| §§11–20 | 40 | 39 | 1 | `batch_02_sections_11_20/` |
| §§21–31 | 44 | 43 | 1 | `batch_03_sections_21_31/` |

Each folder contains `MANIFEST.json`, `RECONSTRUCTIONS.jsonl`, `CONTEXT_LEDGER.jsonl`, and `SECTION_CHECKPOINTS.jsonl`. All 31 sections, including §1 Introduction, §2 Pathology, §15 Bilinear Maps, and §24 Koszul Complexes, were traversed for context. Chapter-scoped definitions and notation are not imported as fresh theorem hypotheses. The nonzero-stalk setup for rank/determinant in §26 is applied only when source-justified.

## Two explicit source holds

1. **§14, L2124 — `lemma-rank`**: The range `{0,1,2,...} ∪ {∞}` is compared literally with the cardinality of an arbitrary basis index set, while locally free modules permit arbitrarily large infinite ranks. Over a point with a field, an uncountably generated free module gives an uncountable cardinality. The convention identifying all infinite cardinals with `∞` is not explicit. Do not silently change the claim or approve without source adjudication.
2. **§27, L4618 — `lemma-simple-invert`**: Item (1) states that elements of the multiplicative system become units in the *original* presheaf `O_X` rather than in `S^{-1}O_X`. Taking a point with `O_X=Z` and `S={2^n}` contradicts that literal claim. Require source clarification before certification.

Both are in `harvest/phase2_chat_stage_a/FURTHER_WORK_NEEDED.jsonl` with exact candidate IDs and reconstruction paths; they are **not** Codex-ready.

## Quality and validation boundary

The complete source statements are preserved in each `standalone_statement_draft`. Contextual expansions have source-line provenance, and the compact `hypotheses` and `conclusions` fields are logical indexing aids; all conditional and enumerated scope remains authoritative in the full statement. A postpass audit repaired a quantifier placement in the principal-parts statement, expanded source-specific referenced setups, and kept two source ambiguities on hold rather than inventing assertions.

- Verified all 110 candidate IDs are unique and active; nine nonactive sources were not promoted.
- All 31 complete source sections have ordered checkpoints, including context-only sections.
- All 108 prepared statements have no unresolved literal `\\ref{...}`; no proof environment text appears in the standalone records.
- Every candidate has `independent_validation="not_started"`, `proof_reviewed=false`, and `phase3_eligible=false`.
- **No broader repository code regression suite or independent Stage B mathematical validation was run.**

## Codex handoff

Codex should read `CHAPTER_MANIFEST.json` and all three batch manifests, and independently validate only records with `decision="reconstruction_completed_awaiting_independent_stage_b_validation"` and empty `stage_a_remaining_work`. Pay particular attention to scoped terminology and logical scope in §26 determinants, §28–§31 differential and cotangent maps, and §29 principal parts. Skip the two holds until source clarification. Do not merge or publish on Stage A authority alone.

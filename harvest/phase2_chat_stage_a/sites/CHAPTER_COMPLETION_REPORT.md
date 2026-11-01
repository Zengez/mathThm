# Sites chapter — completed Stage A source-first preparation
Source: [Stacks Project `sites.tex`, pinned revision `a04446e57ec1fbc252a871afcec7752fb2807b14`](https://github.com/stacks/stacks-project/blob/a04446e57ec1fbc252a871afcec7752fb2807b14/sites.tex).
Branch: `work/sites-source-prepass-20261031`, based on `work/phase2-stage-a-context-enrichment`.
Draft PR: https://github.com/Zengez/mathThm/pull/1

## Final audited counts

| Measure | Count |
|---|---:|
| Physical sections traversed and checkpointed | **52 / 52** |
| Sections with active candidates | **42** |
| Context-only sections (still traversed) | **10** |
| Theorem-like environments in pinned source | **161** |
| Canonical active candidates | **137** |
| Excluded/nonactive source environments | **24** |
| Prior authoritative approved overlap | **0** |
| Active candidates given Stage A dispositions | **137 / 137** |
| **Standalone-prepared for Codex Stage B** | **133** |
| **Further work needed** | **4** |
| Active candidates unprocessed in Stage A | **0** |
| Candidate-bearing sections entirely Stage A ready | **39** |
| Sections with at least one held candidate | **3** (§17, §31, §39) |
| Independent Stage B validations / Phase 3 approvals from this pass | **0 / 0** |

All ten context-only sections are checkpointed (§1, §2, §4, §6, §7, §16, §36, §46, §51, §52). The full authoritative active registry and approvals were cross-checked by candidate ID; nonactive records remain as source leads but were **never** promoted. Earlier theorem-local assumptions are not inherited automatically. The source-scoped ledger includes named situations and notational setups, particularly the inverse-system Situation in §18, presheaf extension functors, localization and slice-topos constructions, stalks, sieves and Grothendieck topology sheafification.

## Six complete source-order batches

| Source sections | Active | Stage A prepared | Further work | Manifest folder |
|---|---:|---:|---:|---|
| §§1–10 | 23 | 23 | 0 | `batch_01_sections_01_10/` |
| §§11–20 | 24 | 23 | 1 | `batch_02_sections_11_20/` |
| §§21–25 | 15 | 15 | 0 | `batch_03_sections_21_25/` |
| §§26–30 | 24 | 24 | 0 | `batch_04_sections_26_30/` |
| §§31–40 | 28 | 25 | 3 | `batch_05_sections_31_40/` |
| §§41–52 | 23 | 23 | 0 | `batch_06_sections_41_52/` |

Each folder has `MANIFEST.json`, `RECONSTRUCTIONS.jsonl`, `CONTEXT_LEDGER.jsonl`, `SECTION_CHECKPOINTS.jsonl`, `A1_REVIEW_NOTES.json` and `CONTEXT_PREFACES.json`. The earlier `harvest/phase2_chat_stage_a0/sites/` folder retains 161 pinned source work packets, a chapter ledger, section checkpoints and canonical eligibility audit. The six manifests record **0 undispositioned active candidates**, keeping `further_work_needed` separate from unprocessed work.

## Four explicitly held source statements

| Location | Candidate | Precise blocker |
|---|---|---|
| §17, L3703 | `lemma-colimit-over-ordinal-sections` | The source statement only specifies cofinality of the ordinal 'large enough', with no bound or quantified size requirement. |
| §31, L7705 | `lemma-relocalize-morphism-topoi` | The statement declares f':Sh(C)/f^-1 G→Sh(D)/F, but F is a sheaf on C, not D. Source codomain is ill-typed; confirm correction to Sh(D)/G before standalone certification. |
| §31, L7788 | `lemma-relocalize-morphism-compare` | The statement sets h_U# = f^-1h_V# for arbitrary c:U→u(V), which is generally false unless U=u(V). Source premise needs adjudication before certification. |
| §39, L9438 | `lemma-criterion-points` | The source condition uses coproducts of representable presheaves h_{U_i} as a map to the final object in Sh(C), without sheafification. A typed comparison needs clarification. |

All four hold IDs have been registered in `harvest/phase2_chat_stage_a/FURTHER_WORK_NEEDED.jsonl` on this isolated branch, with exact packet paths. They are **not** labeled Codex-ready and should be revisited for source clarification rather than silently edited.

## Validation performed and limits

- Reconciled the six batch candidate-ID sets with all **137** canonical active `sites.tex` IDs, comparing source label, source line and original source text. Found **no duplicates, missing active IDs or nonactive promotions**.
- Checked 52 ordered section checkpoints, six manifest counts and all ready/held section mappings. The 10 nonactive section windows remain represented in the context ledger.
- Verified every one of the **133 Stage A-ready** statements contains **no unresolved literal `\\ref{...}`**; no source proof environment markers appear in standalone statements or saved ledger excerpts.
- Confirmed every candidate has `independent_validation="not_started"`, `proof_reviewed=false`, and `phase3_eligible=false`.
- **No broader code regression suite or independent mathematical Stage B validation was run here.** These records are standalone drafts, not independently approved theorems.

## Codex handoff

Codex should load the six batch manifests listed above and process **only** the candidate records with `decision="reconstruction_completed_awaiting_independent_stage_b_validation"`. Skip excluded/nonactive records and the four `further_work_needed` holds. Use pinned source and each record's source statement, scoped context evidence, and proposed hypotheses/conclusions to independently verify exact mathematical equivalence. Do not mark proof review or Phase 3 approval until an independent gate is actually satisfied.

Preserve the working branch isolation until the draft PR is reviewed, and avoid overwriting independently approved records from concurrent work.

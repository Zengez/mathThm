# Simplicial chapter — Stage A source-first preparation complete

**Repository:** `Zengez/mathThm`  
**Branch:** `work/phase2-stage-a-context-enrichment`  
**Pinned Stacks source:** `simplicial.tex`, revision `a04446e57ec1fbc252a871afcec7752fb2807b14`  
**Review date:** 2026-11-01  

## Reconciled population and disposition

- **34 / 34 source sections traversed in order**, including 6 context-only sections without active candidates; 28 sections contain active candidates.
- **106** lemma/theorem/proposition/corollary source environments, **93 active candidate IDs**, **13 excluded from the active pool**, and **0 preexisting authoritative approvals** for this chapter.
- **93 / 93 active candidates** have individually keyed Stage A records; **86** are marked `reconstruction_completed_awaiting_independent_stage_b_validation`, **7** `further_work_needed`.
- **0** independent Stage B mathematical approvals, proof reviews, or Phase 3 promotions performed by this chapter preparation.
- Every record preserves the original pinned statement, candidate ID, source line and label; readiness refers to context reconstruction only, not source-equivalence approval.

## Stage A files to feed Codex

- **Sections 1–17:** `harvest/phase2_chat_stage_a/simplicial/batch_01_sections_01_17/RECONSTRUCTIONS.jsonl` — 18 active candidates, 16 ready, 2 held. Read the companion `MANIFEST.json`, `CONTEXT_LEDGER.jsonl`, and `SECTION_CHECKPOINTS.jsonl` in the same directory.
- **Sections 18–25:** `harvest/phase2_chat_stage_a/simplicial/batch_02_sections_18_25/RECONSTRUCTIONS.jsonl` — 44 active candidates, 41 ready, 3 held. Read the companion `MANIFEST.json`, `CONTEXT_LEDGER.jsonl`, and `SECTION_CHECKPOINTS.jsonl` in the same directory.
- **Sections 26–34:** `harvest/phase2_chat_stage_a/simplicial/batch_03_sections_26_34/RECONSTRUCTIONS.jsonl` — 31 active candidates, 29 ready, 2 held. Read the companion `MANIFEST.json`, `CONTEXT_LEDGER.jsonl`, and `SECTION_CHECKPOINTS.jsonl` in the same directory.

For Stage B, select **exact candidate IDs** where `decision="reconstruction_completed_awaiting_independent_stage_b_validation"`, `stage_a_remaining_work=[]`, and `independent_validation="not_started"`. Do not treat an entire mixed section as ready; avoid the seven held IDs, the thirteen excluded IDs, and any IDs approved before Stage B begins. Keep Stage B independent and source-equivalence focused.

The section-order context ledger distinguishes source notation, definitions, constructions, local theorem data, and the **explicitly invoked** adjunction Situation in §34. In particular, the overcategory diagram used for coskeleta differs from the undercategory diagram used for the left adjoint to truncation; (s), (N), and (Q) carry their appropriate chain/cochain meaning. Source-only `\ref` commands in *ready* candidate drafts and their hypotheses/conclusions have been eliminated.

## Seven outstanding bounded contextual holds

1. **`lemma-face-degeneracy-category`**, source L158: The claim specifies the universal presentation only by citing excluded source Lemma lemma-relations-face-degeneracy (L79). Materialize all five indexed relations explicitly and check their index bounds before labeling standalone. [Candidate record](harvest/phase2_chat_stage_a/simplicial/batch_01_sections_01_17/RECONSTRUCTIONS.jsonl).
2. **`lemma-characterize-cosimplicial-object`**, source L422: Both directions refer to all five relations in excluded Lemma lemma-relations-face-degeneracy (L79), without printing them. Incorporate the relation equations with correct coface/codegeneracy index conventions before declaring a standalone characterization. [Candidate record](harvest/phase2_chat_stage_a/simplicial/batch_01_sections_01_17/RECONSTRUCTIONS.jsonl).
3. **`lemma-work-out`**, source L2427: Verify the construction of the (n+1)-truncated simplicial extension from the matching-face representing functor and make the face/degeneracy maps and claimed adjunction explicit; source L2336-2515 (especially lemma-work-out L2427). [Candidate record](harvest/phase2_chat_stage_a/simplicial/batch_02_sections_18_25/RECONSTRUCTIONS.jsonl).
4. **`lemma-add-simplices`**, source L3128: Unpack excluded Lemma lemma-glue-simplex (simplicial.tex L3083–3127): for each inclusion W^i⊂W^{i+1}, specify the single new nondegenerate simplex x_i in degree n_i, unchanged lower degrees, all higher new simplices degenerate, and its pushout square attaching Δ[n_i] along i_{n_i-1!} sk_{n_i-1}Δ[n_i]. [Candidate record](harvest/phase2_chat_stage_a/simplicial/batch_02_sections_18_25/RECONSTRUCTIONS.jsonl).
5. **`lemma-cosk-shriek`**, source L3201: Verify the precise internal-Hom construction in section 17 and the left-adjoint i_{n!} from L2884–3261; explain why Hom(i_{n!}sk_n Δ[n+1],V)_0 equals the degree-(n+1) matching object in cosk_n sk_n V, and supply n≥0. [Candidate record](harvest/phase2_chat_stage_a/simplicial/batch_02_sections_18_25/RECONSTRUCTIONS.jsonl).
6. **`lemma-homotopy-equivalence-s-Q`**, source L5088: Resolve source wording at simplicial.tex L5088–5103: Q(U),Q(V) are normalized *cochain* complexes by L4334–4364, but the lemma calls Q(a) a homotopy equivalence of *chain* complexes. Verify intended correction and preserve the two conditional conclusions. [Candidate record](harvest/phase2_chat_stage_a/simplicial/batch_03_sections_26_34/RECONSTRUCTIONS.jsonl).
7. **`lemma-map-into-diamond`**, source L5216: Reconstruct the connecting morphism δ(s):C→(A⊕A)[-1] from the degreewise split exact sequence (Homology Lemma homology-lemma-ses-termwise-split), and the compatible sections of diamond A from L5117–5215; verify commutative diagram and uniqueness without assuming a canonical section. [Candidate record](harvest/phase2_chat_stage_a/simplicial/batch_03_sections_26_34/RECONSTRUCTIONS.jsonl).

These seven candidate IDs have also been appended to `harvest/phase2_chat_stage_a/FURTHER_WORK_NEEDED.jsonl`, with the relevant batch manifest as `packet_path`.

## Checks performed

The in-chat source/repository consistency audit passed: JSON/JSONL parsing, all 93 active IDs unique, section coverage 34/34, manifest/record/checkpoint reconciliation, statuses vs. holds, source identity/statement/line/revision equality to pinned Pass 1, no overlap with authoritative approvals, and all seven holds found in the central registry. Ready drafts **and** their separated hypothesis/conclusion fields were checked for dangling LaTeX source references.

The project CLI regression suite and independent mathematical/proof validation **were not run** from this Chat execution. Use this inventory for independent Stage B processing, not as a Phase 3 validation certificate.

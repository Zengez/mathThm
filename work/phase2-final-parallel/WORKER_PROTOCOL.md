# Authoritative Phase 2 — four-worker mathematical review protocol

## Exact scope and independence
Use ONLY the exact candidate IDs in your own worker-N/PENDING.json batches, derived from the audit-verified Stage B and Phase 3 artifacts. The provisional Phase 3 plausible screen selects the queue but is NOT evidence of Phase 2 mathematical equivalence. The Stacks original at the pinned commit is authoritative. Treat source facts in prior Stage A/B notes as aids, not an independent conclusion. Do NOT reread proofs or redo Phase 3 here.

For every candidate, inspect its pinned original Stacks theorem/lemma and the applicable standing assumptions, conventions, and definitions. Check that the proposed final statement is truly standalone, including all hypotheses, quantifier scopes, cases, equivalences, and conclusion parts. Detect changed strength, missing premises, ambiguous notation, and logical-form distortions. Verify the exact Stage B statement, hypotheses, conclusions and logical_form against the original, not merely a hash.

Record your actual reviewer identity or conversation identifier and the prior Stage A and Stage B reviewer identities from the proposal / Stage B row. This is an independent mathematical attempt; a new script/checksum does not establish independence. If reviewer independence cannot be supported, put the record on hold for adjudication.

## Start and checkpoint each complete batch
1. Work ONLY on branch work/phase2-final/chat-N. Verify its commit derives from work/phase2-final/parallel-base. Read this file, your PROMPT.md, your PENDING.json, and the first pending batch.
2. Check first batch's named Stage B, Phase 3 proof review and Phase 2 proposal files against their exact pinned Git blob SHAs. Use python scripts/phase2_final_parallel.py --check --worker N --first-batch for a fast targeted verification (and once initially a full --check --worker N is optional). Never scan whole corpus on every batch.
3. For each candidate_id, locate exactly its Stage B row and associated materialization proposal. Confirm original_source_statement_tex, source_file and line, pinned source revision, Stage A reconstruction, and the Stage B reviewer note. Read the original pinned Stacks source and relevant context. Do not infer mathematical approval from the provisional proof.
4. Write one substantive record per ID to work/phase2-final-parallel/worker-N/decisions/CHAPTER/section-L.jsonl, in the same order as the candidate_ids in that section. Each record has:
   - candidate_id; decision source_equivalence_approved OR source_equivalence_held
   - reviewer and source_first_review: true, proof_reviewed: false
   - prior_stage_a_reviewer and prior_stage_b_reviewer, source_revision, original source file/line, and referenced immutable input paths/SHAs
   - exact final_content fields (statement, hypotheses, conclusions, logical_form; also structured_cases and equivalence_sides if applicable) for approvals, with the approved_content_sha256 computed using scripts.phase2_authoritative.content_digest
   - a substantive semantic_review_note for approvals explaining source equivalence and context, OR a concrete hold_reason and correction/context/adjudication classification for holds.
5. Do not silently edit a Stage B formulation and approve it. For substantive corrections, hold the ID and describe proposed_correction separately. Such corrections need a fresh independent source-first review before central registration.
6. All candidates in a source section must receive a verdict before the section is complete. Record a batch checkpoint at worker-N/checkpoints/BATCH_ID.json with exact IDs and decision counts. Validate outputs and their order against the frozen batch. ONLY THEN remove the completed batch from your own PENDING.json (do not edit immutable ALLOCATION.json).
7. Commit and push your own worker folder changes to YOUR branch. Verify the pushed SHA, then move immediately to the next pending batch without waiting for another user prompt. A new conversation should resume from the first remaining batch using the committed queue/checkpoints. Commit in modest chapter-local batches.

## Strict isolation and authority
Do not edit other worker folders, shared ALLOCATION.json or EXCLUDED.json, authoritative registry, overlays, official Pass 3 files, published catalog, site, main, or the phase3 reconciled branch. Worker decisions are independently reviewed verdicts AWAITING CENTRAL REGISTRATION; do not set phase2_validated, phase3_eligible, pass3_plausible or published. Coordinator will reconcile overlaps/duplicates, source provenance and exact approved-content digests and then use the established Phase 2 authority machinery.

Report the completed and held IDs, section/batch counts, pending work, and the verified remote commit when the conversation ends. Never fake an approval or mark a partial section complete.

# Stage A (Chat) preparation: source-ordered, ledger-driven reconstruction

**Working guidance — October 31, 2026.** This is the operative procedure for *new* Stage A preparation batches on `work/phase2-stage-a-context-enrichment`. It makes explicit the scoped context-ledger method already intended by the section-walk work. See [STAGE_A0_PREPASS.md](STAGE_A0_PREPASS.md) for the optional Medium-thinking preparatory pass. This document does **not** retroactively certify old drafts or change the existing data schema.

## Goal and authority

Stage A (sometimes **A1** when distinguishing it from the new **A0**) uses source-first mathematical analysis to produce an explicitly standalone theorem statement and hypotheses/conclusions for independent **Stage B (Codex)** mathematical validation. Stage A readiness is **not** an independent equivalence judgment, proof check, Pass 3 authorization, or publication.

- Use the pinned Stacks revision `a04446e57ec1fbc252a871afcec7752fb2807b14` and the repository's actual source-section ordering, not a guessed order or an unpinned current upstream file.
- Read the current branch head, section manifests, prior authoritative Codex approvals (the original 655 plus newer approved IDs), and the further-work registry before choosing work. Never regenerate or overwrite a Codex-approved candidate. Reconcile any overlap on the basis of authoritative candidate ID, not filenames or counts.
- Continue at the beginning of the *remaining* Stage A source-order work. Select **whole sections**; include intervening empty/context-only sections in scope accounting even when no candidate output is produced.
- Preserve source statements, candidate IDs, original source locators, Codex records, active pool, and proof bodies. Only prepare candidate review overlays in Stage A artifacts.

## Mandatory running context ledger (not optional section-by-section memory)

**Before** reconstructing candidate statements, maintain an explicit, source-anchored, chronological ledger of the mathematical context actually in force at each candidate's source line. The ledger must advance through *all* intervening source sections, including sections with no active candidates; it cannot be reset at the beginning of an output batch.

1. **Initialize:** From the beginning of the chapter (or a proven, source-revision-matched checkpoint) load globally justified conventions and *explicit* chapter inheritance, with the standing-context atlas and section-opening/label indexes used as **leads**, never automatic hypothesis sources. Carry valid context across output-batch boundaries.
2. **Traverse in source order:** Inspect the chapter and section openings, context-bearing prose, relevant environment boundaries, and all candidate statements; do not inspect proof bodies. Record context introductions, overrides, expiration, references and scope exclusions at their precise source lines.
3. **Differentiate entries:** An actual standing hypothesis or named Situation applicable to a candidate can be materialized as a hypothesis. A definition, notation declaration, theorem already proved, or proof dependency is *not* itself a standing hypothesis. Look up named results only as needed to resolve explicit contextual references.
4. **Scope stack:** Add explicit global/chapter/section conventions only for their justified scope. Push candidate-local quantified objects and assumptions on entry to a lemma/proposition/etc.; pop them when that environment ends. A previous theorem's assumptions do **not** bleed into a later one. Expire temporary examples, cases and constructions at their real boundary. Definitions become available no earlier than their source line.
5. **Chapter transition:** Drop chapter/section-local state on exit. Import cross-chapter context only when the source explicitly inherits it and its guards actually apply. A prior chapter's content is not automatically ambient context.
6. **Candidate snapshot:** At each candidate line, record the exact applicable ledger IDs, any explicitly rejected/expired nearby context, and the source-specific reason for each inherited hypothesis; then reconstruct the statement. Reusing an interpreted Situation across candidates is desirable **only** when its applicability remains established.
7. **Checkpoint:** After each complete section, persist an after-section ledger/checkpoint with its source file, source revision, boundary lines, active scoped context IDs, any unresolved scope questions, and a next-resume locator. Use additional safe candidate-boundary checkpoints as useful. On resumption, validate the checkpoint and any skipped source interval before trusting it.

A context-only section may still be essential to later statements. A section marked `remove` from the *active output* should still have its source interval accounted for when traversing or validating the ledger. No phantom assumptions may be supplied from an unreviewed gap.

### Minimal ledger / checkpoint evidence contract for new batches

Keep a reusable `CONTEXT_LEDGER.jsonl` (or equivalent clearly linked scoped events), and `SECTION_CHECKPOINTS.jsonl` alongside new batch artifacts. For each material entry record at least:

- stable context ID; kind (`standing_assumption`, `named_situation`, `notation`, `definition`, `terminology`, `scope_override`, `scope_end`, `noninheritance_guard`);
- pinned source file, introduction line and pinpoint source reference or excerpt, scope-introduction evidence, effective scope and end/override boundary if known;
- whether it is an *assumption*, an explanation of terminology, or only a lookup lead; applicability conditions and recorded exclusions;
- candidate IDs using the entry (or direct per-candidate ledger-ID links), including any ambiguity for later review.

Each section checkpoint must identify the *post-section* live assumptions/notation, the relevant scope-stack state and line where the following section begins. The ledger is a **review artifact**, not an automatic mathematical inference engine. Never populate it solely by copying a generic chapter description.

For historical batches without these files, derive the ledger from pinned source and relevant earlier checkpoints rather than assuming the old prose notes establish applicability.

## Candidate reconstruction

Use the live ledger and the candidate's own original source statement to expand all safe contextual dependencies into a standalone statement. Make explicit quantified objects, morphisms, bases, diagrams, named setups, and conditions when the source warrants them. Preserve exact logical scope: direction of implications, equivalences, enumerated premises versus conclusions, alternatives, shared existential witnesses, negation, and quantifier dependencies. Do **not** convert definitions or prior facts into extra assumptions, silently strengthen/weaken claims, or erase essential context.

Check source-specific usage of notation/terms, but avoid recursively expanding standard definitions that are not needed to understand the statement. If a source reference or object correspondence requires significant mathematical inference, record a precise blocker rather than fabricating a complete theorem. Errors of commission are worse than conservative incompleteness.

If an A0 overlay exists, treat it as an **unverified working draft**: verify each proposed substitution against the pinned source and current ledger, fix it, or discard it. A0 status alone authorizes nothing.

## Records and labels

Authoritative Stage A outputs continue to live at `harvest/phase2_chat_stage_a/<chapter>/<batch>/MANIFEST.json` and `RECONSTRUCTIONS.jsonl`; unresolved candidate identities also appear in `harvest/phase2_chat_stage_a/FURTHER_WORK_NEEDED.jsonl` with discoverable packet paths. Existing decisions and manifest keys remain authoritative: **do not invent new Stage A readiness decisions** to implement A0.

A candidate is *ready for independent Stage B* only when its Stage A record has:

- `decision == "reconstruction_completed_awaiting_independent_stage_b_validation"`;
- `stage_a_remaining_work` absent or empty; and
- actual source-first mathematical work sufficient to support the standalone draft. A flag alone is not evidence.

Otherwise mark it **`further_work_needed`**, with a concrete missing contextual/semantic issue and source locator. Do not use `codex_reconstruction_needed`; Chat may revisit these later. In section manifests, use `ready_for_codex_validation` only when *all* applicable active candidates meet the gate; reflect mixed/held sections accurately. Keep `context_only` and zero-active sections separate from prepared/validated candidate counts.

Record candidate-specific `context_evidence`, relevant applied ledger IDs, local references consulted, and unresolved conditions in a compatible overlay/sidecar; do not alter original source/proof text. Synchronize manifests, reconstruction decisions, and the further-work registry; never count A0-only work as Stage A ready.

## Before closing a batch

- Confirm all selected source sections are complete, ordered, and accounted for; verify ledger continuity across section, batch and chapter boundaries.
- Confirm every candidate has its original pinned locator and matching candidate ID, and no authoritative Stage B approval was reprocessed.
- Inspect for leaking local assumptions, stale named situations, inappropriate chapter inheritance, and unexpanded implicit premises.
- Check that no `further_work_needed` candidate is labeled ready, and no A0-only candidate enters Stage B counts.
- Check output JSON/JSONL validity and run relevant existing tests/validators when available. Report the tests actually run (do not claim unrun checks passed).
- Commit in bounded batches; report paths, IDs/counts, holds, the last completed section and next source-order resume point. No proof checking or Pass 3 promotion.

## Restart instruction for future Chat sessions

> Read `STAGE_A_PREPARATION.md`, `STAGE_A0_PREPASS.md` (if using A0), the current Stage A manifests and further-work registry, and the pinned Stacks source. Resume in source order, maintain and persist a scope-correct context ledger through context-only and skipped-output sections, and use the actual source-first standalone gate—not a preexisting readiness flag—to determine Stage B readiness. Preserve all prior Codex-approved candidate IDs.

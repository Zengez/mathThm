# Stage A0: Medium-thinking lightweight context pre-pass

**Introduced October 31, 2026.** Stage A0 is an optional, independent *preparation* layer before the existing high-thinking **Stage A (A1)** and independent Codex **Stage B**. It is intended to move repetitive source-context bookkeeping and unambiguous substitutions out of the expensive mathematical-reconstruction pass. The first trial has **not** been executed by this document's creation.

For authoritative Stage A rules, including the mandatory running ledger, see [STAGE_A_PREPARATION.md](STAGE_A_PREPARATION.md). Existing section-walk scope rules, current Stage A manifests, active candidate pool, and Stage B approvals remain in force.

## Mandatory eligibility gate — lesson from the second calibration

**Before choosing ANY A0 source window or generating candidate overlays, check the entire authoritative Phase 2 review history.** The second A0 `varieties.tex` pilot mistakenly selected 10 sections that had already been independently reviewed and approved/held on October 29, because the selection checked Chat Stage A manifests and a 68-record approved overlay snapshot instead of the **full** authoritative registry. See [the second calibration audit](harvest/phase2_chat_stage_a0/varieties/SECOND_CALIBRATION_AUDIT_2026-10-31.md).

- Read `harvest/PHASE2_AUTHORITATIVE_REGISTRY.json`. It specifies **both** `harvest/phase2_authoritative_2026-10-29/APPROVED_OVERLAYS.jsonl` and `harvest/phase2_calibration_2026-10-29/AUTHORITATIVE.jsonl`; a small first-overlay snapshot is **not** the approval universe.
- Check independent section/chapter reviews such as `harvest/phase2_chapters_2026-10-29/varieties_a/INDEPENDENT_VALIDATION.jsonl` and `varieties_b`, alongside later Stage B and Stage A manifests. A chapter can be fully approved or already held **without** appearing under `harvest/phase2_chat_stage_a/<chapter>/`.
- Resolve **three distinct counts**: (i) all theorem-like Stacks source environments, (ii) canonical active candidate IDs from the active registry/verified source coverage, and (iii) canonical IDs **not yet independently approved, held after complete review, or undergoing A1/Stage B processing**. Select A0 windows and report new-work metrics using **(iii)**. Include context-only physical sections for ledger continuity, but do not emit A0 candidate overlays for excluded IDs.
- If approved/held membership or active canonical membership cannot be verified, do **not** claim a valid calibration on unprocessed candidates. Choose another verified window or explicitly label the artifacts as a **non-eligible demonstration**. If zero candidates survive the gate, **stop and reselect**.
- Past holds are not an invitation to reset their adjudication. If a previously held candidate is used as a demonstration, import its hold reason as read-only evidence and keep it excluded from novel A0 workload metrics.

Do not infer eligibility merely from the absence of a Chat Stage A manifest or from a distance of hundreds of sections from the concurrent A1 frontier.

## Operational correction after the Medium calibration (October 31, 2026)

**A0 is a _work-removal_ pass, not a candidate-resolution pass.** Its success metric is how many routine subtasks it has completed for **each** candidate and how directly A1 can use the outputs. Do not optimize A0 for a count of standalone theorems, and do not mistake "no rewrite made" for "nothing useful to do." The October 31 Medium run identified 231 source candidates but missed at least 33 explicit inheritance references and failed to index nine named Situation environments. The corrective audited reference is [the A0 v2 review](harvest/phase2_chat_stage_a0/REVIEW_AND_V2_SPEC_2026-10-31.md), and the retrofitted source packets are in the four `flat` calibration batch directories as `A0_WORKPACKETS_V2.jsonl`. The inherited setup event supplement is `harvest/phase2_chat_stage_a0/flat/CONTEXT_EVENTS_V2.jsonl`.

### Mandatory useful work on every A0 candidate (v2 contract)

1. **Source and identity:** Preserve the original pinned statement, candidate ID and source line; locate its physical chapter/section; check active/canonical and already-approved identities before **any** authoritative stage mutation. If full approval/active registry is unavailable, label the overlay *provisional* and never promote it.
2. **Scoped context walkthrough:** Maintain the chronological context ledger from a verified checkpoint or chapter start, **including `situation` environments**, standing assumption prose, named definitions, local notation and all relevant section openings. Scan context-only/zero-candidate sections as well. Record precise introduction/scope/expiration/override evidence, and make the distinction between source context *available for lookup* and assumptions *actually applicable* to this candidate.
3. **Reference packet:** Detect **all** statement-time `\\ref{...}` references, not just the phrases "Assumptions and notation as in." Explicitly recognize `In Situation \\ref{...}`, `Let ... be as in Definition \\ref{...}`, `With assumptions/notation as in ...`, `as in Example ...`, equation diagrams and nested references. For each relevant reference, retrieve the **full pinned referenced setup environment** (not merely a short citation string), its line, type, exact label, and scope. Capture follow-on nested setup references one level deeper when inexpensive; stop when inference is required. Store missing target labels for A1, never mark them silently resolved.
4. **Mechanical statement breakdown:** Extract literal statements of *given objects*, local declarations, visibly enumerated premises, visibly stated conclusions, equivalence/alternatives, named notation and quantifiers. Preserve source text and line/character offsets. A literal `before Then`/`after Then` partition is **only a cue**, not a verified hypotheses/conclusions split, especially with multiple implications or enumerated equivalents.
5. **Safe context assembly:** Prepare an **A0 proposed preface** or explicit candidate-local context fragment by copying source-backed setup clauses where identity and scope are unambiguous. This can remain a detached addition rather than a fully rewritten theorem. Mark each proposed insertion with exact provenance; copy the named Situation and inherited definitions *as source material* even where applicability needs A1 verification. Do not smuggle definitions or results into theorem hypotheses.
6. **Concrete A1 handoff:** Record `easy_tasks_completed` with evidence and `a1_remaining_tasks` with explicit work type, necessary source references, the exact issue that blocks safe completion, and a practical next step. Never use one generic "verify everything" note as a substitute for extracting readily available dependencies.
7. **Checkpoint and reconcile:** Preserve complete sections, source-ordered context and context-expiration events across output batches. Keep A0 work packets in their own namespace and never assign `stage_a_readiness`, existing Stage A `decision`, Codex approval, or Pass 3 status.

**Do the simple work even on a complex candidate.** A candidate with a hard object identification can still have its source references resolved, hypotheses transcribed, notation mapped, and multiple logical equivalence groups identified. A0 should not mark the entire candidate blocked merely because its final standalone reconstruction is difficult.

### Output interpretation

For new runs, include `A0_WORKPACKETS_V2.jsonl` (or an equivalent with the above fields) as the primary deliverable in addition to `CONTEXT_LEDGER.jsonl`, `SECTION_CHECKPOINTS.jsonl` and `MANIFEST.json`. It should carry `source_dependencies` with exact excerpts, `source_literal_structure`, `easy_tasks_completed`, `a1_remaining_tasks`, and `a0_work_profile`. Old labels `a0_no_changes_needed` and `a0_expanded` remain only backward-compatible metadata; **they do not measure whether the easy work has been done**. Summarize coverage by actual completed subtasks (full reference retrieval, inherited setup packet collection, structural breakdown, candidates with precise holds, unresolved source lookups) rather than a ready count.

A0 must **not** spend its effort on detailed theorem equivalence, proving referenced lemmas, subtle scope adjudication or recursively expanding all standard terms. Its job is to make those questions well-posed for A1 and minimize rediscovery.

## Pipeline and trust boundary

```text
Pinned Stacks source + authoritative approved-ID index
    ↓
A0 (Medium): source-ordered context ledger, safe expansions, exact unresolved notes
    ↓   [A0 overlays only — no readiness promotion]
A1 / Stage A (High): verify against original source, complete hard reconstruction,
    │                flag further_work_needed or authoritative Stage A-ready
    ↓
Stage B (Codex): independent source/semantic validation
    ↓
Future proof/Pass 3 gate (not part of A0 or Stage A)
```

**A0 never verifies a candidate as standalone, never authorizes Stage B, and never changes or reproduces Codex-approved records.** A0 performs no theorem proof checking, public publication, duplicate-merger adjudication or candidate-pool edits.

## Intended first experiment

Select an **unoccupied source-order window comfortably ahead of the concurrently advancing A1 frontier**. Roughly 200 candidate-bearing sections ahead was only an arbitrary collision-avoidance buffer, **not** an exact-count gate or benchmark requirement. Use actual manifests and latest progress to pick any adequately separated, unprocessed whole-section interval. For the initial calibration the intended trial size was **40 candidate-bearing sections**, using roughly ten per checkpoint. When starting mid-chapter, inspect earlier material needed to reconstruct scope, including intervening context-only sections; do not reprocess old candidate overlays or infer applicability from a skipped gap.

Before selection, inspect the *latest* branch, the authoritative Codex-approved ID lists (including the original 655 and subsequent approvals), Stage A manifests, current source-order frontier and active candidate registry. Avoid overlap with concurrent A1 processing. If the jump starts mid-chapter, reconstruct the ledger from the chapter start or a verified, pinned, scope-complete checkpoint; **never begin with an empty or assumed ledger**. A full-section walk can reuse source indexes as leads but must verify applicable context. On changing chapter, reset local state and use only explicit inheritance.

## What A0 should do, in source order

1. **Read the original statement and trusted context leads.** Load pinned Stacks source revision `a04446e57ec1fbc252a871afcec7752fb2807b14`, chapter/section openings, exact labels, reviewed standing-context atlas, prior validated ledger checkpoint, active IDs and authoritative approvals. Indexes are locator aids, not mathematical authority.
2. **Build/update a scoped ledger.** On encountering a source declaration, record its exact locator, text/faithful excerpt, scope evidence, applicability, active interval, type and overrides. Distinguish standing assumptions from definitions, notation, proof dependencies and candidate-local hypotheses. Handle context-only sections and expiration explicitly; push/pop local mathematical environments and record negative (do-not-inherit) evidence. Save full-section checkpoints.
3. **Perform safe, low-inference edits.** Substitute an explicitly applicable Situation; restate an inherited section/chapter hypothesis; introduce an already defined symbol, object, morphism or base; resolve an exact, unambiguous local reference; make a clearly implicit quantifier explicit. Keep standard mathematical terminology concise rather than recursively expanding all definitions.
4. **Preserve logical form.** Keep `if`/ `only if`, equivalences, enumerations, existential witness sharing, quantified scope, alternatives, and subordinate hypotheses exactly as the source requires. Stop before any expansion demanding a substantial mathematical argument or uncertain correspondence.
5. **Write an overlay, not a verdict.** Preserve exact original statement, proposed partial/full expansion, applied ledger-ID/source links and a transformation list. Name each unresolved issue concretely with the first source label/location needed for A1. Partial progress is useful; do not hide uncertainty under a generic `needs more work` without a specific reason.
6. **Checkpoint and proceed.** Save after every full section, including sections with no active candidates; skip writing candidate overlays for already Codex-approved identities, but still account for any context-bearing section where those candidates appear. Commit each bounded batch independently.

### Good A0 work

A section says `Throughout this section, let R be Noetherian and M a finite R-module`; a later candidate states `If M is flat, M is projective`. If the source and scope confirm both assumptions persist, A0 can propose `Let R be a Noetherian ring and M a finite flat R-module. Then M is projective.` The source lines and context IDs must be attached. A1 still checks correctness and standalone fidelity.

### Stop/hold examples

- `By Lemma X the map is an isomorphism` without a clear object substitution. Locate Lemma X, record the exact missing object correspondence, and defer.
- A theorem-dependent proof fact mentioned in surrounding prose; do not turn that fact into a premise.
- A temporary assumption used in the prior lemma; pop it rather than inheriting it.
- An ambiguous interpretation of a numbered equivalence, local notation, or a shared existential witness; retain source form and flag the specific ambiguity.
- A section's introductory discussion that says `we often assume` but does not actually impose a condition on this candidate; do not apply it automatically.

## Output location and minimal schema (A0 only)

Use a separate namespace, e.g. `harvest/phase2_chat_stage_a0/<chapter>/<batch>/`, with:

- `MANIFEST.json`: A0 schema/version, reviewer + thinking level, pinned source revision, exact source interval, complete section ordinals (including zero-active/context-only), candidate IDs/counts, prior Codex-approved IDs skipped, checkpoint paths, continuation cursor, and A0-only status counts.
- `CONTEXT_LEDGER.jsonl`: source-anchored additions, scope ends, overrides, guards, entry type, applicable intervals and stable IDs. Preserve events sufficient to reconstruct each candidate's live context.
- `SECTION_CHECKPOINTS.jsonl`: one per traversed complete source section, post-section live IDs and scope stack, next source line/section, source revision, unresolved scope changes.
- `A0_RECONSTRUCTIONS.jsonl`: per-candidate original source text and pinned locator, `a0_status`, partial standalone draft, exact applied-context IDs, source-backed transformations, remaining issues, suggested A1 checks, and difficulty estimate.
- An optional `REPORT.md`: processed physical and candidate-bearing sections, A0 statuses, errors/holds, and comparison measures.

Example **illustrative** candidate overlay (not a current candidate or required exact machine schema):

```json
{
  "schema": "maththm.phase2.chat-stage-a0.v1",
  "candidate_id": "candidate.stacks.EXAMPLE",
  "source_file": "example.tex",
  "source_revision": "a04446e57ec1fbc252a871afcec7752fb2807b14",
  "source_line": 1234,
  "original_source_statement_tex": "...",
  "a0_status": "a0_unresolved",
  "proposed_standalone_statement": "...",
  "applied_context_ids": ["example.tex:1100:standing-setup"],
  "transformations": [
    {"action": "insert_explicit_section_setup", "context_id": "example.tex:1100:standing-setup", "source_line": 1100}
  ],
  "unresolved": [{"issue": "Object correspondence for Lemma 4.2", "reference": "example-lemma-4-2"}],
  "a1_next_check": "Verify how the referenced morphism specializes"
}
```

**A0 statuses (sidecar only):**

| `a0_status` | Meaning |
| --- | --- |
| `a0_expanded` | All straightforward expansion attempted; may still be semantically incomplete or wrong; **requires A1** |
| `a0_unresolved` | Useful partial expansion with explicit remaining blockers |
| `a0_no_changes_needed` | No mechanical expansion found; **not** a standalone certification |
| `a0_blocked` | Cannot safely proceed without a source/context/identity issue being resolved |

A0 may also attach *non-authoritative* difficulty `simple`, `moderate`, `difficult`, or `blocked` for A1 batching. Do **not** use or change the existing `decision`, `stage_a_remaining_work`, `stage_a_readiness`, independent-validation flags, or `harvest/phase2_chat_stage_a/FURTHER_WORK_NEEDED.jsonl` to express A0 progress. Do not count A0 as Stage A prepared, Codex ready, Codex completed, or Pass 3 eligible.

## A1 consumption and promotion

A1 should read the A0 original+proposed statements, transformed-context provenance, ledger/checkpoints and unresolved notes **alongside** the pinned original source. For each A0 substitution, verify applicability and logical equivalence. Resolve difficult issues or record **`further_work_needed`** with a precise source locator. Only then produce the established `harvest/phase2_chat_stage_a/...` `RECONSTRUCTIONS.jsonl` and `MANIFEST.json`. The *existing* Stage A ready gate remains:

```text
decision == "reconstruction_completed_awaiting_independent_stage_b_validation"
and stage_a_remaining_work is absent or empty
and source-first mathematical reconstruction was actually completed
```

Merely consuming an `a0_expanded` file does not satisfy this. Stage B independently validates; no A0/A1 overlay can approve itself or enable proof screening.

## Pilot quality and stop rules

After the 40-section experiment, independently audit a representative set of 10–15 candidate overlays with High thinking, including seemingly simple/complete entries *and* unresolved cases. Compare against A1-only sections when possible: mechanical coverage, reusable applied context, fraction needing mathematical repair, wrong/inapplicable assumptions introduced, A1 review effort, and time/effort saved. Audit any actual errors before scaling to 100–200 candidate-bearing sections. If Medium outputs repeatedly introduce untraceable or incorrect hypotheses, tighten or suspend A0; conservative omissions are preferable to invented theorems.

## Future-chat quick start

> We are running the **Stage A0 Medium-thinking pre-pass** for `Zengez/mathThm`, branch `work/phase2-stage-a-context-enrichment`. Read `STAGE_A0_PREPASS.md` and `STAGE_A_PREPARATION.md`. Inspect latest source-order frontier and authoritative Stage B approvals; select the next safe full-section window, rebuild/continue the pinned, source-anchored, scoped context ledger, and perform only mechanically justified expansion. Write A0 overlays under `harvest/phase2_chat_stage_a0/`, checkpoint every section, never set Stage A readiness, and leave the mathematical questions explicitly for A1. Do not start Stage B or proof checking.

# mathThm — initial bulk harvesting design discussion

**Discussion state: October 28, 2026.** This file records a proposed minimal three-pass acquisition process and the decisions the user has explicitly agreed to. It is **not an implementation**, engine authorization, or permission to begin harvesting. The user wants to avoid the mathDef research-pipeline scope escalation. Aim first for at least a couple hundred real results before redesigning the theorem UI.

## Settled principles

1. The **initial goal is a large, reasonably credible theorem/reference collection**, not a rigorous mathematical proof audit. False positives in the earliest candidate pass are acceptable.
2. **Three narrow passes**: a very fast theorem/proof-locator harvest; an interpretation pass that splits hypotheses/conclusions; and a short proof-plausibility screen.
3. **Never do deep research as an unintended side effect of any pass.** The Pass 3 stop rule is particularly strict.
4. **Source confidence and proof-screening confidence are separate fields.** An established mathematical reference may be a more credible provenance source, but that does not mean an assistant verified a proof.
5. Preserve full source-faithful theorem statements, a direct source/anchor and a **precise retrievable proof reference**. Preserve the original intact while extracting searchable fields. Reuse source-level metadata rather than repeating it by hand for every theorem.
6. Pass 2 should handle statements such as "with assumptions/notation as in Lemma 4.2": attempt a cheap **local textual cross-reference expansion** where clear, record the cited prerequisite locator and what text was recovered, and never invent hypotheses if context cannot be recovered. This is extraction, **not mathematical research**. Keep unresolved statements in the candidate/triage queue rather than silently creating a possibly false searchable claim.
7. Do not use multiple proof locations or theorem dependencies as an excuse to crawl recursively through mathematics. No semantic deduplication or deep proof-method classification in the first bulk run.
8. Wikipedia can be a valuable **discovery map**: theorem names, subject lists, category/backlink structures and references. It is not by itself evidence that every mathematical article provides a proof. Source selection should optimize fast, repeatable theorem/proof extraction. Source-specific licensing/attribution must be checked at the source-policy level before republishing substantial verbatim text.

## Pass definitions (settled intent)

### Pass 1 — very-low-reasoning, source-native harvesting

- Identify text that looks like a mathematical theorem/lemma/proposition/corollary and a nearby item that **looks like a proof**.
- **Do not read, inspect logical steps, or assess the quality of the proof.** Identifying a proof heading, section, anchor, or attached argument is enough.
- Capture the *full* mathematical statement and citation/locator of the proof, plus source ID/URL and a stable candidate key. Preserve statement wording faithfully and identify any unavoidable context dependency without resolving it yet.
- Allow substantial false positives: claims may be exercises, unproven proposals, incomplete proofs, bad mathematics, duplicates, etc. Keep them as **candidates**, not certified site records.
- The same source may yield many candidates; avoid reopening it for every entry where a single source-level extraction will do.

### Pass 2 — medium-reasoning statement structuring

- Extract **hypotheses** and **conclusions** and obvious side-specific tags from the preserved statement.
- For local "as in Lemma 4.2"/"under the preceding assumptions" cases, retrieve the referenced local text **if immediately available**, and preserve its location/wording. This is a bounded text extraction, not a proof investigation or research into implications.
- Preserve the original theorem statement; do not manufacture independent assumptions when the logical structure is ambiguous.
- If a prerequisite is not cheaply recoverable, mark the candidate `needs_context`, keep its location, and do not spend time recursively finding all prerequisite results.
- Do not research truth, validate proof or compare equivalent formulations.

### Pass 3 — short proof-plausibility screen

Read the actually referenced proof with a **hard stop** on effort, unfamiliar dependencies, or necessary extra research. A source being unfamiliar is NOT itself evidence of a false theorem.

Outcomes agreed with the user:

| Outcome | Criterion | Meaning |
| --- | --- | --- |
| **plausible / provisionally true** | Complete the intended quick pass through the proof without seeing an evident issue | Reasonably credible to include in a clearly labeled provisional theorem collection; **not** mathematical verification |
| **questionable** | The scan has to stop or truncate because needed follow-up, references, mathematical background or other analysis would exceed its strict budget | Status is inconclusive; record what stopped the scan and the location needing follow-up |
| **rejected** | The scan finds a **positive, identifiable issue** | Record the observed reason and source location; do not simply reject because of unfamiliar notation, difficulty or an unsupported impression |

**Important distinction:** a bad *proof* is not necessarily a false *theorem*. If a cited proof is rejected, keep the statement and provenance as a candidate for another source/proof when appropriate. "Rejected" is initially a verdict on the harvested statement-plus-proof evidence, not an assertion that the theorem is mathematically false. Conversely, a plausible proof is merely "not obviously bad after a bounded scan," not proof of validity.

Pass 3 may include only minimal additional mathematical reference consultation needed to clarify a specific immediate issue. It must never develop into a dependency cascade. Source confidence remains independent.

## Operational proposals to discuss before implementation

- Use a source-specific batch and stage outputs, rather than a general autonomous theorem-research framework. A small persistent file/manifest for each stage should suffice; do not build a complex dependency graph or adjudication system.
- Stage 1 creates candidates, Stage 2 adds searchable annotations and context-needed flags, Stage 3 records evidence and the verdict. Keep the original extract immutable and attach supplemental fields.
- Proposed public catalog policy: **only provisional/plausible, fully structured results** are promoted to the current accepted JSON schema. Keep questionable, rejected-evidence and needs-context items in separate audit/candidate queues, retaining complete provenance. This is a recommendation, not yet specifically confirmed by the user.
- Do not make accepted-schema validator treat a Pass 1 proof-heading detection as equivalent to an inspected Pass 3 proof. Existing `acquisition.status=cursory_screened` is assigned only after actual inspection; a future Pass 3 verdict may require an additive metadata field for `plausible`, `questionable`, or `rejected` with a brief issue note.
- Prefer first bulk pass targeting hundreds of source-backed candidate items and **at least 200–300 provisionally accepted results** if available. This is a target, not a guaranteed yield.
- Measure actual time and accepted yield per stage and reject/stop reasons. If Pass 3 dominates cost, keep its strict limit rather than adding deeper mathematics. Checkpoint each source or bounded batch, not individual tokens or research subproblems.
- No interface redesign before a meaningful multi-hundred-result corpus. The current mathDef V2 linker and theorem record contract are ready to consume accepted entries.

## Remaining choices worth settling

1. **Visibility of questionable items**: recommendation is to keep them in the separate candidate queue (with reasons) and publish only plausible/structured entries in the current site. The user has not explicitly decided whether to display questionable entries with an extra warning.
2. **Exact per-proof screening budget**: choose a small fixed bound for follow-up lookups / extra time / maximum dependency depth when implementing. It can be source-adjusted but must remain explicit and measured; no unlimited research.
3. **Candidate storage and source strategy**: select the simplest transport (JSONL or similarly simple files), source-locator conventions and batch checkpoint format after deciding which initial sources to use. Avoid re-creating mathDef's multi-phase research framework.
4. **Copyright/licensing**: use source-level attribution/reuse rules for full-text candidate capture and eventual public display; where verbatim publication is inappropriate, retain locator and a faithful restatement with a transcription flag, rather than silently mislabeling it an exact quote.

## Next gate

Discuss the remaining choices, especially the public treatment of `questionable` candidates, and explicitly approve the minimal implementation before creating a harvesting engine or starting the bulk pass. Update WORK_CHECKPOINT.md with subsequent decisions.

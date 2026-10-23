# mathThm — future features and deliberately deferred ideas

**Recorded:** 2026-10-23  
**Purpose:** keep interesting future designs discoverable WITHOUT accidentally expanding the initial prototype or slowing rapid theorem acquisition. Consult PROJECT_PLAN.md for requirements already agreed for the near-term prototype.

This is a **backlog/idea file**, not an implementation authorization. Whenever an item becomes a current task, move or reference it in the active checkpoint with explicit user approval and tests.

## A. Complex Boolean hypothesis/conclusion queries — AFTER INITIAL AUDIT

Within each side (Hypotheses and Conclusions), allow users to add rows vertically. The first input has no Boolean dropdown; successive rows have a compact **AND / OR** selector and a text input. Users can change grouping using indentation, a nested-group UI, parentheses, or another clear interaction. Use explicit expression trees internally so grouping/precedence is never ambiguous. Display the interpreted Boolean expression to catch misunderstandings.

Illustrative requested logic:

    (Compactness AND Completeness) OR (Closed AND Bounded AND Real)

A second illustration: a nested OR alternative within part of an AND expression, with other AND constraints outside it. The user's prose examples were exploratory and not a binding indentation grammar. Mathematicians can handle complex nesting, but the UI must clearly signal scope.

The two large columns themselves have an **AND** connector initially; an **AND / OR** selector between columns may be added later. Do not mistake that top-level operator for one of the individual search terms. On mobile retain a clear grouping and relation between columns.

This sophisticated query builder is **explicitly deferred until after the initial audit**. Do not spend prototype-development effort building it.

## B. Semantic and mathematical search improvements

- Better normalized aliases, lemmatization, irregular inflections, possessives, and notation-aware matching. Domain-specific alias tables should supplement (not overtrust) ordinary English stemming. Keep mathematical meanings distinct when a familiar word has multiple technical uses.
- Reuse mathDef canonical term IDs and alternate formulations for search expansion where safe. Search concept-tag provenance: exact-text vs author/tag-derived vs reviewer-approved additions.
- Improve mathematical-context disambiguation rather than automatically expanding every homonymous term.
- Search for **theorems with weaker hypotheses** than a selected theorem, or **stronger conclusions** under the same assumptions. This requires genuine mathematical entailment/relationships, not keyword overlap, and therefore belongs to a later reviewed semantic layer.
- Optional refinement filters by domain, proof status, source, historical context, proof method, or complexity, only if useful to users.
- More intelligent relevance ranking and mathematically faithful preview generation with explanations for tag-only matches.
- Natural-language questions interpreted as structured searches, always showing the effective conditions for user inspection.
- Search against explicit implication directions in logical equivalences, maintaining **one displayed theorem record**, and later auditing extracted directional relations.

## C. Multiple proof perspectives, after proof audits

Long-term objective: a theorem can have a **Proofs** section showing genuinely different mathematical methods of proof, not a pile of substantially equivalent rewordings.

Possible labels: algebraic, geometric, topological, analytic, combinatorial, constructive, probabilistic, categorical, etc. These labels should be assigned carefully by editors; a proof may span several domains. The rigorous audit can compare alternative accessible proofs, record validity and assumptions, and determine whether the mathematical methods are fundamentally different. Store proof provenance, source locator, source statement, and audit status for each.

During duplicate consolidation, preserve distinct proofs and earlier sources when theorem records are deemed mathematically equivalent; do not collapse scopes that are actually different.

Later consider displaying complete proofs directly on the site when licensing, accuracy, rendering, attribution, and editorial work permit it. **Do not reproduce proofs in the first prototype**; link to accessible proofs.

## D. Theorem dependency graph

Eventually record that a proof of Theorem B uses Theorem A, perhaps as directed dependencies, with context and confidence/evidence. It may support proof exploration, topic maps, source discovery, and related-result browsing.

Reserve conceptual schema room now, but **do not compute or infer theorem dependencies in the prototype or initial ingestion**. Evaluating whether the proof actually depends on another result takes careful mathematical analysis; distinguish cited theorems from necessary dependencies. Learn from mathDef's dependency-first work without importing its mathematical source content.

## E. Theorem variants, equivalence classes, and editorial history

- Alternate mathematically equivalent statements or standard formulations retained alongside the source original and rationale.
- Equivalence-class reviews and carefully audited duplicate merges; preserve proof/source provenance.
- Distinguish generalizations/specializations from genuine equivalence rather than merging based on title or text similarity.
- History of edits, suggested reformulations, approval/rejection, and mathematically significant wording changes.
- Directional statements for equivalence theorems and conditional branches without making unsound logical claims.
- Optional "compare versions / alternative hypotheses" display.

## F. Public corrections and community involvement

- Suggestions for an omitted theorem, wrong hypothesis/conclusion extraction, inaccurate tag, bad proof locator, questionable mathDef link, theorem reformulation, mathematical error, or a novel independent proof.
- Use a review queue with explicit accepted/revised/deferred/rejected statuses and explanatory rationale.
- Optionally support no-GitHub-account submissions with anonymous or optional attribution, with careful spam/security/privacy design. GitHub issue drafts are an acceptable initial pragmatic intake mechanism.
- Context-specific feedback for nested/expanded definitions and, eventually, individual proof approaches.
- Display appropriate warnings when entries are merely cursory screened vs mathematically audited or verified.
- Community corrections inform reviewer decisions, never automatically overwrite mathematics.

## G. mathDef and cross-project evolution

**Already implemented in mathDef as of 2026-10-23:** a versioned, SHA-256 content-addressed **production definition snapshot and manifest** (see https://github.com/Zengez/mathDef/blob/main/DEFINITION_EXPORT.md). mathThm does not yet contain a consumer.

Potential improvements:
- Publish a separate reviewed/approved channel for independent mathDef Wave 2, only when appropriate; never silently mix distinct research corpora.
- Delta manifests listing changed definitions to reduce downloads further.
- mathDef-originated push-style "updated" signals/webhooks for consumers, supplementing basic polling and content-hash checks.
- Shared canonical term-matching and contextual variant-resolution package.
- A mathDef-owned scanner/queue for mathematical concepts in mathThm that are missing from mathDef, with source/context/provenance. mathDef may independently source and add approved definitions, after which mathThm's refreshed snapshot enables the link. No automatic write-back from mathThm.
- Broader interoperability among future math-related repositories while keeping them independently auditable.

## H. Shared UI, common tooling, and performance

- General-purpose cross-project UI component library after confirming the currently portable mathDef design can be safely reused. Avoid refactoring mathDef active research simply to serve mathThm.
- Portable, domain-configurable corpus-ingestion engine, checkpointing, source/proof locator verification, schema validation, browser preview, and audit tools for future mathematical education projects.
- Incremental search indexing and client-side performance refinements as corpus size grows; benchmark before adopting heavier search infrastructure.
- Richer math rendering, source/proof preview cards, mathematical notation search, accessible keyboard navigation, and UI localization only after foundational usability is proven.
- Optional integration across concept/definition/theorem/proof graph views, with careful editorial distinction between a mathematical relation and text similarity.

## I. Long-term quality, trust, and completeness

- Layered audit workflow checking existence, claimed completeness, actual correctness, generality, special cases, source fidelity, proof techniques, and duplicate equivalence.
- Clear confidence/review status for each claim. An AI cursory look, an automated audit, a mathematical human review, and peer-reviewed publication are *different* forms of evidence.
- Reference and licensing metadata, including decisions about what proof text or theorem statements may be reproduced.
- User-facing review history and transparent origin trail, where appropriate.
- Retention of discarded/repaired claims in audit logs to allow reproducibility.
- Curated domain coverage and completeness metrics after aggressive broad collection; never advertise unreviewed theorems as guaranteed accurate.

---

## Deferment guardrails

1. **No advanced Boolean editor during the initial prototype or aggressive ingestion.** It is slated for after the audit process.
2. **No proof correctness requirement during first population.** Only inspect an actually accessible proof enough to determine it appears to claim completion, and retain precise reference.
3. **No theorem dependency graph in the first prototype.**
4. **No automatic editing of mathDef definitions by mathThm.**
5. **No extensive duplicate/equivalence/proof-method classification while aggressively collecting.** These are later audit steps.
6. **No assumption that documentation equals implementation or that the user authorized work by recording an idea.**

For scheduling and the current state, use WORK_CHECKPOINT.md; for immediate agreed scope, use PROJECT_PLAN.md.

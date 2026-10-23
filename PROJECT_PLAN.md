# mathThm — authoritative project plan and design contract

**Established:** 2026-10-23  
**Repository:** https://github.com/Zengez/mathThm  
**Companion repository:** https://github.com/Zengez/mathDef  
**Document status:** original planning contract. For the current implementation state see [WORK_CHECKPOINT.md](WORK_CHECKPOINT.md) and [PROTOTYPE_IMPLEMENTATION.md](PROTOTYPE_IMPLEMENTATION.md).  
**Historical authorization when first written:** documentation only. The user subsequently authorized Phase 1 prototype implementation on 2026-10-23. Do not interpret this older planning note as the current status; read WORK_CHECKPOINT.md.

This document reconstructs the decisions from the design discussions that preceded implementation. A new chat should read this document, WORK_CHECKPOINT.md, and FUTURE_FEATURES.md before making changes. Where this document calls something a **decision**, treat it as settled unless the user changes it. Where it calls something a **recommendation**, **proposal**, or **deferred choice**, use engineering judgment or discuss if material. Do not silently expand scope.

---

## 1. Objective, scope, and principles

mathThm is a mathDef-family research and educational website/catalog for **mathematical results**: theorems, lemmas, propositions, corollaries, and other proven statements. Do **not** restrict collection to explicitly named or labeled "theorems." The theorem's mathematical statement is primary; a conventional name/title is optional metadata, not a search field or a required identifier.

The core reader question is:

> "Given these hypotheses, what theorems can establish this kind of conclusion?"

Unlike mathDef's separate "term name" and "definition text" searches, mathThm searches **hypotheses** and **conclusions**. Its two searches work together on a **single list of unique theorem results**, with an AND operator between the two sections by default. With only one section populated, search just that section.

Example (the original conversational example was accidentally reversed, then corrected): a user knows **compactness** and wants information about **orbits**. They enter "compactness" under Hypotheses and "orbit" under Conclusions. This is an illustrative search, *not* a claim that compactness by itself proves a fact about orbits.

Priorities, in order:
1. Correctly represent and make discoveries possible through the **hypothesis/conclusion division**.
2. Maintain exact mathematical statements and enough **source/proof provenance** for subsequent human mathematical review.
3. Make a usable, mathDef-like prototype with roughly **20 deliberately varied real results**.
4. After the prototype is approved, **collect aggressively and quickly**, deferring substantive correctness checks to later audits.
5. Reuse portable infrastructure and maintain resumable, auditable processes so future sister projects benefit.
6. Eventually enable user suggestions and multiple verified, mathematically distinct proofs.

The **initial collection is not a mathematical certification exercise**. The prototype is a research draft and must be labeled accordingly. Completeness, proof correctness, equivalence, contextual interpretation, and editorial polish are later audit objectives.

---

## 2. Project boundaries and relationship to mathDef

### Canonical responsibility

- **mathDef owns definitions**: term IDs, names, aliases, alternative formulations/contexts, definition text, citations, and its own definition review/intake procedures.
- **mathThm owns mathematical results**: theorem records, hypotheses, conclusions, searchable tags, original-statement provenance, and references to accessible proofs.
- mathThm must **not automatically add definitions to mathDef**. When a theorem uses a concept not defined there, record it as unresolved for future mathDef-owned scanning/review and possible addition.
- When mathDef later adds such a definition, mathThm can discover it via a refreshed snapshot and link it. User-requested missing terms remain suggestions, never automatic accepted definitions.
- This division should generalize to later mathematical reference projects.

### Existing mathDef integration infrastructure

On 2026-10-23, the mathDef repository gained a **production** definitions export and a content-hashed manifest, documented in:

https://github.com/Zengez/mathDef/blob/main/DEFINITION_EXPORT.md

Expected published URLs:
- https://zengez.github.io/mathDef/api/definitions/v1/manifest.json
- https://zengez.github.io/mathDef/api/definitions/v1/snapshot.json

The associated mathDef commit was d695056e0e5659ebb702d954fff8b86d5cc35411. Its GitHub Pages and metadata-audit workflows reported success. The live URLs were not independently retrieved using the prior connector; verify public fetch behavior when developing the consumer.

The manifest supplies a SHA-256 content version, snapshot path, and count. A future mathThm consumer should check/revalidate the small manifest and **only pull the full snapshot when its hash changes**, verifying the bytes before atomically switching to the new local cached version. If the fetch or checksum fails, retain the last valid snapshot. Unchanged content should not force re-downloading; a changed Git commit without changed exported definitions need not cause a refresh. A simple consumer-build check or periodic polling is adequate initially; push notifications, delta streams, and sophisticated synchronization can wait.

**Critical boundary:** this v1 feed represents mathDef's **production definitions**. Its independent Wave 1 and Wave 2 reconstruction research is **not automatically included**. Do not silently confuse or merge those corpora. Reassess if mathDef later publishes or promotes a different dataset.

The snapshot carries stable definition IDs, labels/aliases, source text, alternate formulations, and contextual dependency links, suitable for building inline expandable definition displays. The algorithm to identify links from theorem prose to mathDef concepts belongs on the mathThm side; use existing mathDef data and portable matching techniques, with conservative disambiguation. If source offsets for accurate inline placement are unavailable, insert an explicit definition control near the relevant text or below the paragraph rather than guessing offsets.

### Visual portability

The sites should look unmistakably like the **same author's related projects**: reuse mathDef's motif, typography, spacing, color, panel/card patterns, responsive behavior, feedback UI, and expansion affordances as much as practical. Different data/search mechanics are expected, but the visual family resemblance is a high priority.

At the time of planning, mathDef already has a **portable display-only interface** in research_pipeline/ui/ with template, styles, JS, feedback, renderer, and branding configuration. Inspect its current state before reuse. Its documentation distinguishes UI reuse from mathematical data reconstruction. Reuse those UI pieces or derive a theorem-specific adapter; do not import an independent mathDef research corpus as if it were mathThm theorem data. Avoid destabilizing mathDef's active research workflows to extract or refactor a shared package. Favor controlled reuse first, generalized reusable packages later.

---

## 3. Prototype UI and expected behavior

### 3.1 Main search controls

Use **two obvious, side-by-side columns** on desktop:

- **Hypotheses** — "What do I know?"
- **Conclusions / Results** — "What do I want to establish?"

Between the columns show an unmistakable **AND** joiner. It is the operator *between the two sections*, **not** an item of either hypothesis list. On small screens, stack the sections while retaining a clearly visible connector between them.

In the immediate prototype there is **one free-text query in each column**, searched in real time (subject to sensible debouncing if needed). Blank means no restriction. The two nonblank queries must both match their **respective** search sides on the same theorem record.

Future possibility: allow AND/OR **between the two columns**, but the immediate implementation defaults to AND and need not implement this dropdown yet.

### 3.2 Advanced multi-clause UI — explicitly deferred

Eventually each column can grow **vertically** with multiple text input rows. The first row has just a text input; each additional row has a compact AND/OR dropdown plus an input. Users can group/indent rows to express nested Boolean logic. Example intended expression:

    (Compactness AND Completeness) OR (Closed AND Bounded AND Real)

Another example may mix nested AND, OR, and parentheses. **Indentation was only an illustrative UI thought**, not necessarily the underlying syntax. Prefer an explicit nested Boolean expression/tree and an unambiguous visual grouping mechanism, perhaps accompanied by a rendered logical expression to make precedence clear. Allow the user to adjust grouping. There is no need to design or implement this sophisticated editor until **after the initial audit process**. Keep a forward-compatible internal query model when possible without adding prototype complexity. See FUTURE_FEATURES.md.

### 3.3 Search is text + tags, not proof inference

For each theorem, independently match:
- Hypotheses query against text extracted/indexed from the **hypotheses** and the theorem's **hypothesis tags**.
- Conclusions query against text extracted/indexed from the **conclusions** and the theorem's **conclusion tags**.

Use both ordinary case-insensitive text matching and conservative linguistic normalization / lemmatization (including common morphological variants and possessives). "compact"/"compactness" should be discoverable together where mathematically appropriate; some variants such as "run"/"ran"/"running" need more than suffix stripping. Avoid crude stemming that corrupts mathematical distinctions. Store canonical/normalized searchable tag keys, and normalize incoming search terms using compatible rules. An alias dictionary can cover mathematical phrases that cannot be reduced by English stemming. mathDef labels and aliases can contribute to future term normalization or disambiguation.

**Tags are first-class from the beginning**, not only a post-audit feature. Capture both directly expressed concepts and useful **additional discovery concepts** (possibly absent verbatim from the theorem statement). Keep enough internal provenance to distinguish source-derived tags from later proposed/editor-approved additions, to help with audits. If a user reports that a theorem should appear for a search term, the correction workflow can add an approved side-specific tag.

Do not pretend that matching a tag establishes a new mathematical implication or that a search is an automated theorem prover. In the prototype the structured fields/tags are indexed editorial interpretations that may require mathematical audit.

### 3.4 Presenting results

There is **one combined result list**. The same theorem must appear **once**, even when several conditions, tags, equivalent implication directions, or proof sources match.

Initial display threshold suggestion (accepted provisionally): **10 results**.
- **10 or fewer hits:** show full theorem statements by default.
- **More than 10 hits:** show **compact, relevant previews** by default, with per-result expansion and global "Show all/Expand all" control.
- A user should be able to override the automatic compact/full selection.
- Previews show enough context to preserve which parts are assumptions and which are consequences, without growing longer than the full record. If no useful reduction is possible, show the full short theorem rather than a misleading excerpt.
- If a **tag** matched but the literal term is absent from the excerpt, explicitly show the matched concept/tag or a small note ("Matched conclusion tag: ...") so the result is not puzzling.
- Retain a visible link to the accessible proof source after the theorem statement (no proof reproduction in the initial prototype).
- Optional theorem title/name is useful for conventional named results but never required and does not warrant a separate search bar.

**Primary theorem display**: use the mathematically faithful **unified source statement** rather than forcing the user to read a theorem broken into two separately rewritten prose panels. Hypotheses/conclusions are structured *behind the scenes* for search and highlighting. If useful, labels can appear in previews, but do not unintentionally modify logical scope/quantifiers in a canonical display.

### 3.5 Definition expansion in theorem text

Clicking a recognized concept in a theorem should display a **mathDef definition without leaving the theorem page**. Preserve the mathDef style of collapsible/nested/in-line exploration where sensible, with proper contextual variant prioritization. Recursive expansion inside an opened definition can use mathDef's own dependencies while suppressing cycles and already visible ancestor terms.

Theorem-to-definition links target **existing mathDef stable IDs**, not theorem-to-theorem links. A missing term is an unresolved candidate, not a silently invented mathThm definition. Don't require new terms be added to mathDef before the theorem can be included.

---

## 4. Theorem records: conceptual schema and source fidelity

This is a **logical schema recommendation**, not a preordained database format. Choose Markdown/LaTeX plus metadata, JSON, or another maintainable format during implementation. Aim for fast ingestion and fast client-side search without losing exact wording or audit trails. Metadata extraction should be automated wherever safe.

Each theorem record should support:

| Field / grouping | Purpose / requirement |
| --- | --- |
| Stable theorem ID | Never identify records solely by title or search content. |
| Canonical displayed statement | Full mathematical statement, faithfully sourced, readable with LaTeX. |
| Original source wording / locator | Retain exact accessible original wording whenever legally appropriate; retain exact location and transformation record. |
| Editorial status / transformation history | Log any rewording, why, by whom/process, and whether equivalence has been reviewed. |
| Optional name/title | Useful conventional name, not mandatory and not a search column. |
| Mathematical subject/context | Helpful domain labels for provenance/disambiguation. |
| Hypotheses and conclusions | Independently searchable, faithful structured extraction / representations. |
| Hypothesis and conclusion tags | Side-specific normalized concepts plus original labels and origin/provenance. |
| Searchable implication directions | To handle equivalences and multiple outcomes while displaying one theorem once. |
| Source reference(s) | URL, work, author/publisher where available, theorem/page/section locator, retrieval details where helpful. |
| Proof reference(s) | **Accessible** proof URL and sufficiently precise locator to find the proof again. |
| Proof cursory-screening status | Whether a visible, seemingly finished proof was located; NOT a correctness judgment. |
| Later audit state | Mathematical correctness, equivalent variants, tag accuracy, duplicate review, and approved corrections. |
| mathDef references | Canonical term IDs, context selection if known, unresolved definition candidates. |
| Provenance/time | When/how discovered, source permission/attribution information, ingest batch/checkpoint. |

If a source statement is carefully reformulated, retain the original alongside the edited statement and explicit reason/flag. **Default for initial intake is to preserve the original mathematical statement as closely as possible** (with only necessary technical formatting); editorial rewrites belong mainly in a later audit. Exact mathematical wording, quantifiers, topology, object type, and exception clauses are essential.

Avoid copying nontrivial copyrighted proof text. Mathematical facts are not protected as such, but a particular author's expression may be; educational/research uses can affect fair-use analysis, not give blanket permission. Keep attribution, licensing/provenance metadata, and preserve exact source wording where permitted. Proof **links** are the default.

### Non-implication and equivalence cases

Do not assume every theorem fits "a single list of assumptions implies a single conclusion." Support:
- Multiple hypotheses and conclusions.
- Equivalences, e.g. P iff Q iff R: index each of P, Q, R as eligible **hypothesis concepts and conclusion concepts**. Better still, retain which implication directions are valid. A matching user should see **one theorem record**, not multiple near-identical results.
- More complex nested quantifiers or logical relationships: preserve the intact authoritative statement even where extracted fields are initially imperfect.

Extraction and tagging must not silently claim logically independent combinations are valid if the source only establishes specific directions. Search-facing representations are for retrieval; deeper implication modeling is an audit/deferred capability. Never reconstruct a supposedly stronger theorem merely by combining tags.

---

## 5. Initial proof requirement and deliberately permissive screening

**This requirement is unusually important and was reiterated by the user.**

For an initial theorem to enter the searchable corpus, an investigator/agent must have actually **accessed and visually or textually inspected a proof** and confirmed merely that it **claims to be a completed proof** of the identified result, not just:
- an unsolved student exercise / instructions on how to begin;
- a proposed proof outline with no actual proof;
- an unfinished student draft;
- a proof ending obviously in mid-sentence or with a promised section/case missing entirely.

That is essentially the whole initial proof check. **Do not** review logical soundness, omitted edge cases, hidden hypotheses, mathematical elegance, conventional correctness, or equivalence of all formulations during aggressive intake. The user specifically expects a significant share of initial proof references to be flawed; that is acceptable for a **draft prototype**. An inferior proof may be replaced or augmented by a better accessible proof during later review.

A merely plausible bibliography entry, paywalled/unretrievable citation, or claimed proof in a document the agent cannot actually access is **not sufficient** for the searchable initial set. Such a theorem can go into a separate **candidate queue** without a claim of a proof having been screened. The proof source should be directly retrievable, or have a precise location (section/page/theorem ID) within an accessible document; the key standard is ability to **return to the actually viewed proof** in the audit, not necessarily a dedicated single-proof URL.

Suggested states:
- Candidate discovered; proof not yet inspected.
- Proof located/accessed.
- Cursory screened: appears to present a finished proof; eligible for draft corpus.
- Audited: mathematically reviewed, unresolved findings may remain.
- Verified: passed a clearly defined rigorous-review standard (and later human review if required).
- Rejected/needs correction: audit result, with rationale and preserved provenance.

Never confuse the "cursory screened" status with mathematical endorsement. Initial UI must clearly describe the whole content as an unverified research draft.

### Multiple proofs and duplicate records

Retain **several proof references** per theorem from the beginning, even though the prototype displays at most links. Long-term the user wants multiple proofs **only when they use fundamentally distinct mathematical approaches**, with headings/categories such as geometric, algebraic, analytic, etc. Determining that classification is **after thorough mathematical audit**, not an ingestion-time burden.

Initial collection can admit duplicate/near-duplicate theorem records. Exact identical duplicate submissions can be detected almost for free, but **do not spend significant ingestion time identifying mathematical equivalence**; this belongs to the audit. When two records are later judged mathematically equivalent, consolidate thoughtfully:
- preserve both source statements, references, and editorial history;
- inspect all associated proofs;
- retain genuinely different proof approaches as separately described references/versions;
- retain potentially meaningful different hypotheses, scopes, or formulations rather than merging based on superficial textual similarity.

---

## 6. Community correction and review model

Follow the general mathDef idea: readers can suggest missing results, missing search tags, erroneous hypothesis/conclusion classification, inaccurate theorem text, erroneous definition links, better mathematical formulations, problematic proof references, or other corrections.

**No submission edits accepted content automatically.** The maintainers and assistant review and explicitly approve/reject/defer suggestions. Track contributor identity/optional attribution where permitted; GitHub-backed suggestion intake can be an initial pragmatic path. Anonymous or account-free submissions are desirable eventually, not an initial blocker.

A suggested *equivalent theorem reformulation* may be mathematically subtle. Preserve the source statement and proposal separately, review whether they are truly equivalent, and track approval rationale/versions. Never silently replace original text with a user suggestion.

For the first UI prototype, reuse feedback infrastructure if inexpensive. Full moderation/correction workflows belong to subsequent stages; don't let them slow core UI or bulk ingestion.

---

## 7. Phased workflow and priorities

### Phase 0 — documentation (CURRENT / this request)

Create this PROJECT_PLAN.md, FUTURE_FEATURES.md, README.md, and WORK_CHECKPOINT.md. **No source code, theorem population, deployment, or other implementation**. Record the exact resume state. Stop.

### Phase 1 — inspect portability and build a 20-result working prototype (NEXT, only after explicit user go-ahead)

1. Inspect the current mathDef portable UI, its display contract, styles, and branding config; identify what can be safely reused. Do not disrupt mathDef active Phase 2 work.
2. Confirm mathDef definition-feed public URL, manifest JSON, snapshot hash, and consumer viability. Build a read-only cached consumer only as part of explicitly authorized implementation.
3. Choose about **20 genuine, varied mathematical results**, not a random same-type sample. The user has not specified particular theorems and authorized the assistant to select test cases once implementation begins.
4. Ensure the chosen real results have proof references actually accessible and minimally screened as described above.
5. Cover: simple implications, multiple assumptions, multiple conclusions, equivalences, an unnamed result, a named theorem, different math fields, mathematical notation/quantifiers, a relevant mathDef term/alias link, an unresolved term, and search/tag-only matches. Not every case must be independent; aim for useful coverage.
6. Implement the basic two-column search + AND semantics, matching across text/tags with conservative normalization, responsive layout matching mathDef, sensible result threshold and compact/full controls, proof-source links, and basic mathDef inline definition expansion.
7. Evaluate search quality and user experience. Fix prototype issues **before** launching the aggressive collection phase. Keep the mathematical content labeled unverified.

**Prototype acceptance guidance:** two-field queries return the right **single** list of theorem IDs; blank-field queries work; a result is not duplicated by multiple tags or equivalence directions; >10 compact mode and <=10 full mode work; expand controls work; proof sources are accessible; math renders; definition opening stays in page; visual continuity with mathDef is recognizable; the provenance of every sample theorem is inspectable. Tests should specifically cover equivalence indexing, tag-only matches, dangerous over-stemming, and snapshot-update fallback.

### Phase 2 — design and tune aggressive, resumable collection

Only after the user reviews the prototype:
- Establish candidate/source workflows; choose broad mathematical resources containing accessible finished proofs.
- Prioritize **throughput**, proof-access confirmation, precise locators, source-attribution preservation, and enough structural extraction for the two search fields.
- Use persistent checkpoint files, stable IDs, idempotent re-runs, bounded batches, interruption-safe writes, and progress logs. A new chat should be able to resume from the most recent checkpoint without reconstructing extensive history.
- Measure batch yield, throughput, rejection categories, unresolved mathDef links, proof accessibility, and indexing health. Optimize proven bottlenecks.
- Keep the initial mathematical evaluation **deliberately superficial**. Do not turn ingestion into the expensive proof-correctness audit.

### Phase 3 — deep audit and refinement (later)

Separate, explicit review passes for mathematical correctness, assumptions/quantifiers, statement-to-source fidelity, proof validity, hypotheses/conclusions/tags, equivalence/duplicate consolidation, and alternative proofs. Maintain rationale, uncertainty, audit state, and community correction proposals. Prune or repair erroneous results after audit; the initial discovery catalog is not a promise that all entries will survive.

### Phase 4 and beyond — deferred ecosystem features

See FUTURE_FEATURES.md for complex Boolean grouping, semantically weaker assumptions/stronger conclusions, proof classification, theorem dependency graphs, personalized search, richer community feedback, cross-project missing-definition discovery, and general-purpose portable framework improvements. Do **not** implement these simply because the architecture permits them.

---

## 8. Development and preservation requirements

- **Always keep this plan and the checkpoint current.** Before a long batch or substantial change, save enough structured state for another chat to resume. Use small commits and verify what landed; do not claim unverified implementation success.
- All content collection and auditing must distinguish **discovered candidate**, **accessible proof screened**, **mathematically audited**, and **verified**. Never inflate status.
- Prefer readable, stable IDs, explicit schemas, and deterministic outputs; preserve information needed for future reversals and merges.
- The old mathDef production reference and ongoing independent Wave 2 workflow are separate; do not make incidental writes to mathDef while implementing mathThm.
- Match the existing mathDef styling first rather than inventing a visually unrelated UI.
- Keep performance in mind: normalize/index once at build time where possible, normalize incoming search consistently, and cache definition snapshots safely. Avoid premature complex semantic search infrastructure.
- User-facing corrections and alternative theorems require editorial acceptance, not automatic content modification.
- GitHub workflow and site publication mechanisms should be selected in Phase 1. Nothing is currently deployed from mathThm.

---

## 9. Explicit settled decisions versus open engineering choices

**Settled:** all proven results are in scope; separate hypothesis/conclusion searching with AND by default; two columns; blank query unrestricted; text + side-specific tags with conservative normalization; no separate name search; optional titles; 10-result initial threshold; short but mathematically faithful previews; full source-statement display; definition expansion linked to existing mathDef; source/proof record sufficient for later retrieval; proof must actually have been accessed during cursory screen; preserve mathematical wording as closely as possible; initial corpus remains unverified; duplicate/equivalence analysis deferred; multiple distinct proof strategies as a later objective; approx. 20 varied real sample results before bulk ingestion; visually near-identical theme to mathDef; fully resumable processing and portable scripts; later user correction workflow.

**Design discretion, not yet fixed:** exact theorem file format, search tokenizer, precise normalization/alias tables, which mathDef UI modules to copy/adapt, exact excerpt algorithm, grouping semantics of future Boolean editor, accessible-proof source mix, initial 20 theorem choices, source-license handling in difficult individual cases, and eventual graph/proof-classification standards.

**Do not mistake deferred ideas for current requirements.** The user repeatedly insisted that advanced Boolean UI and rigorous proof review should not delay the initial prototype or rapid population.

---

## 10. Handoff when context is lost

When resuming in a new chat:
1. Read README.md, this document, WORK_CHECKPOINT.md, and FUTURE_FEATURES.md from the **live mathThm repository**.
2. Read current mathDef DEFINITION_EXPORT.md and inspect current research_pipeline/ui/ **only as needed for the next authorized phase**.
3. Check the latest GitHub commits and any on-disk checkpoint files against WORK_CHECKPOINT.md. Prioritize repository state over memories of prior chats.
4. Restate what is built versus only planned, and what the user has authorized next.
5. Continue from the last durable checkpoint. Before stopping, update the checkpoint with file paths, tests, pending actions, and explicit next step.

**Historical note:** when this plan was first written, only documentation was authorized. Phase 1 implementation was subsequently authorized and begun. See WORK_CHECKPOINT.md.

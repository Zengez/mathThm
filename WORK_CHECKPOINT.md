## October 28, 2026 — three-pass theorem harvesting design (discussion only)

**New reference:** [HARVEST_DESIGN.md](HARVEST_DESIGN.md). The user endorsed a very low-reasoning Pass 1 that saves full theorem statements and merely **apparent** proof locations (no proof reading), followed by Pass 2 to separate hypotheses/results and cheaply resolve local assumptions such as “as in Lemma 4.2,” followed by a strict-stop Pass 3 that scans the actual proof only for immediately evident issues. Pass 3 outcomes are **plausible/provisionally true** (quick scan completed without evident issue), **questionable** (scan truncated because necessary follow-up exceeded budget), and **rejected** (positive identifiable issue). Preserve the distinction between source confidence and proof-screening confidence and between rejected *proof evidence* and a false *theorem*.

**Not authorized:** harvesting-engine implementation, corpus harvesting, proof research, interface redesign. These remain for the next design/implementation decisions. Recommended default (pending user approval): only fully structured plausible entries enter public accepted records; questionable/needs-context/rejected-evidence candidates are retained separately. Collect 200–300 provisional results before revisiting UI decisions. See HARVEST_DESIGN.md for assumptions, caveats and open questions.

---

## October 28, 2026 — linking and theorem schema completed; harvesting-engine design is NEXT

**User direction:** Finish definition linking and theorem-record schema now. Explicitly **do not build the collection engine yet**; discuss a much smaller, more efficient engine first because mathDef's initial pipeline grew disproportionately complicated. After the engine is agreed, collect at least a couple of hundred real theorems BEFORE revisiting substantial UI/performance design choices. No bulk theorem collection performed in this tranche.

**Definition linking completed (mathThm only):**
- Introduced indexed trie-based source-text phrase matching in `web/definition-links.js`; built once from mathDef V2 term headings and aliases rather than evaluating thousands of regexes against each rendered theorem. It preserves repeated occurrences, matches whole phrases only, and always prefers the longest relevant phrase. It reserves ambiguous/ancestor-blocked spans as plain text so their interior words cannot generate misleading links.
- Small explicit, reviewed-in-code adjective aliases include `continuous` → original ID `topology.continuity` and `uniformly continuous` → `analysis.uniform-continuity`, plus compact/connected/closed, resolved through the **canonical mathDef V2** index. Auto names are indexed, with subject-based disambiguation only if uniquely resolvable; explicit per-theorem link hints override same-length automatic matches. Unresolved ambiguous terms are left unlinked rather than guessed.
- General UI `web/app.js` uses this matcher in theorem text and every expanded formulation. Existing V2 ancestor suppression remains active, including legacy aliases; no mathDef changes.
- Regression tests in `tests/test_definition_links.cjs` cover Heine–Cantor, multiword preference, multiple occurrences, ambiguous labels and ancestor protection; `tests/test_v2_browser.cjs` also checks with the real V2 snapshot that `continuous` and `uniformly continuous` are distinct clickable targets.

**Theorem schema completed (additive/backward-compatible):**
- Kept outer `maththm.theorems.v1` for frontend compatibility; added `contract_revision:2`, explicit `entry_type`, statement/source provenance (including nullable verbatim transcription and exact locator), minimal proof inspection evidence, acquisition batch and screening status, independent mathematical audit state, tag origins/annotations and optional link exclusions/proof candidates.
- Converted all **existing 20** sample records without editing theorem statements, side tags or accepted proof links. One previously listed alternate proof URL is now explicitly an `uninspected` candidate, not falsely called screened. The original statements are recorded as **editorial restatements not independently audited** and no verbatim source transcription is fabricated.
- Wrote the contract in `THEOREM_RECORD_CONTRACT.md`. Added `scripts/theorem_schema.py` validation integrated into `scripts/build_site.py`, and `tests/test_record_schema.py` negative and positive regression coverage. The validator enforces accepted proofs genuinely marked cursory-screened, stable IDs, traceability and separate mathematical audit, but NEVER assesses mathematical truth.
- Removed a few literal "20 theorems" assumptions from tests/site notices so the accepted catalog can grow, without undertaking interface redesign.
- **Current gate:** finish verifying the latest CI browser and GitHub Pages deployment, then obtain the user's preferences for a minimally bureaucratic bulk harvesting process. **Do not write such an engine or begin harvesting until discussed.** The user prefers collecting 200+ real results before revisiting the interface.

## October 28, 2026 — recursive mathDef expansion path fix

**User report:** Expanding "subspace topology" in mathThm could offer a clickable link to itself inside the newly expanded definition, allowing repeated recursive expansion. Requested parity with mathDef's currently implemented ancestry exclusion.

**Root cause:** mathThm's general prose auto-linker did not receive the current expansion ancestry, whereas its separate structured dependency buttons had partial path filtering. The two paths disagreed, and V2 canonical/legacy aliases were not uniformly checked.

**Implemented in mathThm only:**
- `web/mathdef-v2.js`: exported `branchPath` and `visibleDependencies` helpers. They canonicalize IDs using the published V2 adapter, suppress ancestors on the active expansion path (including the current term), reject missing/duplicate dependencies, and enforce the existing depth limit.
- `web/app.js`: carries `data-def-path` on all generated inline definition buttons, passes the canonical branch to every displayed formulation (including alternatives), filters both phrase links and explicit nested dependency buttons, and rejects programmatic cyclic clicks. Longest-phrase matching reserves an unavailable ancestor phrase as plain text, avoiding a misleading smaller link within the blocked phrase.
- `tests/test_mathdef_v2.cjs`: canonical-alias self-link, A→B→A, depth, separate-branch reuse, duplicate dependency checks.
- `tests/test_ui_smoke.cjs`: simulated browser clicks opening "Subspace topology" then "Topology"; checks the self and ancestor links are absent in the generated HTML while non-ancestor links remain accessible.

**Behavioral scope:** Followed mathDef's **current** `research_pipeline/ui/app.js` code, which explicitly suppresses only ancestors on the active path and permits a sibling term in another sibling's definition. Older `DEPENDENCY_LINKING.md` text describes broader sibling blocking; the current code governs this implementation. No changes were made to mathDef.

**Verification:** `https://github.com/Zengez/mathThm/actions/runs/40707944171` completed successfully, including JavaScript syntax, Node/ Python tests, verified mathDef V2 snapshot bundling and GitHub Pages deployment. The public mathThm URL remains `https://zengez.github.io/mathThm/`. A manual browser visual follow-up is useful, but automatic regression checks pass. Continue normal prototype feedback; bulk theorem acquisition is not authorized by this bug fix.

---

## October 28, 2026 — mathDef v2 consumer migration

**User authorization:** Update mathThm to use the *published cleaned mathDef v2* feed, not v1. Preserve theorem corpus and search behavior; do not undertake bulk theorem collection. This entry supersedes the older October 23 prototype v1 notes below.

- `scripts/build_site.py` consumes `https://zengez.github.io/mathDef/api/definitions/v2/`: validates manifest schema (`merged`), SHA-256, payload shape, all meanings and formulations, official Subject metadata, historical original IDs, and redirect registry. It bundles the verified `mathdef-snapshot.json` and `mathdef-manifest.json` on every main-branch/nightly Pages build.
- `web/mathdef-v2.js` resolves canonical group headings, original mathDef IDs and all three retired ID aliases from `consolidated_ids`; `web/app.js` uses the adapter for theorem hints, auto phrase links, and recursive context-specific expansions. An exact official Subject is preferred; explicit target-formulation overrides are honored for nested links; all other formulations remain available in the expandable alternatives. Actual per-formulation links are followed, rather than the possibly unrelated heading aggregate.
- When the bundled snapshot cannot be fetched, the browser attempts the LIVE **v2** endpoint with SHA-256 integrity checking, never silently reverting to the old original-only v1 feed. Theorem search and source/proof links stay usable without mathDef.
- New tests: `tests/test_mathdef_feed.py`, `tests/test_mathdef_v2.cjs`, updated browser-like `tests/test_ui_smoke.cjs`; GitHub Pages workflow now refuses release without a verified v2 bundle, validates theorem hint IDs against its original aliases, checks SHA and field counts, and retains the nightly schedule.
- The canonical source of definitions remains mathDef. No mathDef content is imported into mathThm's theorem dataset or edited by this migration.

**Next task:** continue normal mathThm prototype review when user returns. Future mathDef publishes will be consumed on mathThm's next nightly or manual site build. In particular, historical theorem IDs should be resolved by mathDef's v2 `original_ids` and consolidated redirect tables, not copied into new mathThm sources.

---

# Current work checkpoint — October 23, 2026

**Phase:** 1 — first prototype deployed; automated checks and UI boot test passed. Awaiting user review of live interface.  
**Next authorized action:** Review live site at https://zengez.github.io/mathThm/ , test interactions/visuals and refine the prototype with the user. **Do not begin aggressive collection or mathematical proof audits without further authorization.**

## Implemented

- 20 genuine, source-attributed, cursory-screened mathematical results in data/theorems.json, across nine subject labels. Each contains a source/proof URL and explicit unverified status; no deep mathematical correctness claims.
- mathDef-themed website (web/index.html and styles.css), two side-specific searches joined by AND, blank-side unrestricted, lemma/theorem/proposition-ready record structure, proof links, term definitions expandable in page.
- web/search-core.js: conservative inflection/alias handling, side-specific tags, equivalence indexing, and 10-result compact/full cutoff.
- web/app.js: theorem cards, full/compact controls, source/proof links, mathematical rendering and recursive mathDef expansion.
- scripts/build_site.py: builds _site and verifies/publicly bundles the mathDef **production** snapshot. In its first CI build, it successfully bundled 1,014 mathDef definitions. Independent Wave 1/2 mathDef experimental data remains separate and untouched.
- tests/test_data.py and tests/test_search.cjs; GitHub workflow .github/workflows/pages.yml executes them on main, manually, and on a nightly schedule.
- PROTOTYPE_IMPLEMENTATION.md records implementation, corpus and setup/limitations.

## Verified GitHub Actions results

- **Latest validated and deployed code**: https://github.com/Zengez/mathThm/actions/runs/39978765020 — **success**: syntax, Node search and UI boot tests, Python corpus checks, generation, SHA-256 mathDef snapshot, upload and Pages deployment. GitHub repository metadata now reports Pages enabled.

- Initial build: https://github.com/Zengez/mathThm/actions/runs/39977407748 — **all script syntax, Node search, Python data, build, SHA-256 snapshot, output-file steps passed**; configure-pages failed because GitHub Pages was not enabled.
- Automatic Pages enablement attempt: https://github.com/Zengez/mathThm/actions/runs/39977542990 — build steps passed; configure-pages failed with **"Resource not accessible by integration"**, requiring owner activation in repository settings.
- Repo owner should go to https://github.com/Zengez/mathThm/settings/pages and select **GitHub Actions** under Build and deployment → Source, then run https://github.com/Zengez/mathThm/actions/workflows/pages.yml on main.
- Intended site URL: https://zengez.github.io/mathThm/ — **deployment reported successful** by GitHub Actions; end-to-end live-browser visual testing is still outstanding.

## Tests/next review tasks

1. GitHub Pages is enabled and latest tested deployment succeeded; independently exercise the live URL and verify the bundled mathDef snapshot in browser.
2. Test literal and normalized searches, tags, AND vs blank-side behavior, compact/full at 10 results, one-result-per-theorem, Heine–Borel equivalence direction.
3. Check mathDef in-page expansion of "compact", "continuous", and other terms, nested paths and cycle protection, and source/proof links. Confirm mobile/desktop style resembles mathDef. Automated tests do not substitute for browser testing.
4. Fix discovered issues, update tests and checkpoint, then seek user prototype feedback and approval before starting any bulk acquisition.
5. Keep FUTURE_FEATURES.md deferred; write a distinct resumable collection pipeline only when approved.

**Mathematical and provenance caveats:** The 20 sources were assessed solely for the existence of a superficially completed accessible proof. Statement wording is flagged as condensed/restated with original source links; formal equivalence, correctness and proof reasoning were NOT audited. Some source pages explicitly warn that they need mathematical proofreading.

---

## Historical Phase 0 checkpoint (superseded below)

# mathThm — durable work checkpoint / resume instructions

**Checkpoint date:** 2026-10-23  
**Current phase:** 0 — documentation only  
**Current authorization:** Create durable planning, future-ideas, and handoff records in mathThm. **Do not begin any implementation or theorem collection yet.**  
**Project branch:** main  
**Repository:** https://github.com/Zengez/mathThm

## Live status (as of this checkpoint)

| Work item | Status |
| --- | --- |
| Verify mathThm repository access and push permission | Completed, authenticated Zengez account |
| Agree on mathThm purpose and prototype scope | Completed through October 23 conversations |
| Prepare consolidated development/design document | Completed: PROJECT_PLAN.md |
| Record explicitly deferred future features | Completed: FUTURE_FEATURES.md |
| Create new-chat navigation and resume file | Completed: README.md and this checkpoint |
| Implement any mathThm site/UI code | **Not started; not authorized yet** |
| Acquire or insert the first 20 sample theorems | **Not started; not authorized yet** |
| Write ingestion, search, feedback, or audit scripts | **Not started; not authorized yet** |
| Connect mathThm to mathDef snapshot | **Not started in mathThm; pending future implementation** |
| Deploy/publish mathThm website | **Not started** |
| Bulk theorem collection or mathematical audit | **Not started; intentionally later stages** |

## Related completed work in mathDef (not in this repository)

On 2026-10-23, mathDef received a reusable, **production-only** definition export with a content-addressed change manifest. The implementation was committed as:

https://github.com/Zengez/mathDef/commit/d695056e0e5659ebb702d954fff8b86d5cc35411

GitHub reported success for both mathDef's standard Pages publication and corpus metadata audit. Docs: https://github.com/Zengez/mathDef/blob/main/DEFINITION_EXPORT.md

Expected feed paths:
- https://zengez.github.io/mathDef/api/definitions/v1/manifest.json
- https://zengez.github.io/mathDef/api/definitions/v1/snapshot.json

**Important:** No mathThm-side consumer is built yet; verify real-world public fetch, caching, format, and checksum when authorized to implement the prototype. mathDef's independent Phase 2/Wave 2 research is active separately; keep it untouched unless the user explicitly directs work there.

## What to do at the beginning of the NEXT authorized work session

1. Read the four root documents, especially PROJECT_PLAN.md and the "Deferment guardrails" in FUTURE_FEATURES.md.
2. Verify GitHub main HEAD, file contents, and any more recent checkpoints; do not assume this file is newer than subsequent commits.
3. Confirm the user has explicitly requested implementation, rather than another design-only or planning-only conversation.
4. When authorized, begin **Phase 1**: inspect mathDef's existing portable UI at research_pipeline/ui and its current display branding/adapter files, then plan a mathThm-compatible skin/search workflow. Verify the mathDef production snapshot endpoint and consumer contract; do not modify mathDef's Phase 2 work.
5. Select **approximately 20 varied real results with actually accessible cursory-screened proofs**, then implement/test the side-by-side hypothesis/conclusion AND search, tags/text matching, faithful unified theorem display, compact/full switch at 10 hits, math rendering, proof links, and inline mathDef definition expansions.
6. Stop for user testing and UX refinement **before** authorizing aggressive collection, or follow later explicit instructions.
7. Update THIS FILE with new stage, date, summary, commit SHA(s), tests, blockers, and exact next action before ending or doing lengthy processing.

## Core requirements to preserve verbatim in spirit

- Initial proof check = **accessible proof actually examined; appears to present a finished proof**. It is **not** a correctness audit or a check that all mathematical cases were addressed. Store exact link+locator for later review.
- Initial theorem statement = preserve source wording as closely as reasonably/legally possible. If changed, retain original/locator and explicit editorial change log.
- Search = **Hypotheses AND Conclusions** (separate side-specific text/tags). Blank side unrestricted; never return duplicate display cards for equivalent implication directions.
- Visual identity = close to mathDef; reuse its already-portable UI where appropriate.
- Later audit = rigorous proof review, equivalence/duplicate consolidation, mathematical tag validation, alternative independent proof perspectives.
- Deferred Boolean group builder (multiple AND/OR clauses within columns) = **after initial audit**; its conceptual UI examples are preserved in FUTURE_FEATURES.md.

## Working conventions for subsequent long tasks

- Use small, well-scoped commits and a persistent checkpoint.
- Log candidate and proof-screening statuses separately from verified mathematical correctness.
- Maintain resumable processing and idempotency before large-scale ingestion.
- Keep sample/prototype and production-scale/audited data distinguishable.
- Do not overwrite a more recent decision with an older plan; document changes and their rationale.
- No background work is presumed; each assistant chat must verify completion and record exactly what was done.

## Last work completed in this chat

Created project-only documentation on mathThm's main branch:

- README.md — orientation and links
- PROJECT_PLAN.md — consolidated design, settled choices, workflows and acceptance checks
- FUTURE_FEATURES.md — deferred feature backlog
- WORK_CHECKPOINT.md — this resumption record

**Next action:** hand the documentation back to the user. Wait for an explicit instruction to begin the prototype; no code or math content has been written by this initial planning step.

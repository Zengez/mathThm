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

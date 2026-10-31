# Sites and Sheaves — source-ordered A0 work packet (2026-10-31)

Pinned revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`. Source: `sites.tex`. Isolated branch: `work/sites-source-prepass-20261031` (from `work/phase2-stage-a-context-enrichment`).

## Coverage and scope

- Traversed all **52 physical sections** in source order, including **10 context-only** sections.
- Extracted **161 proof-adjacent theorem-like source statements**, with reproducible candidate IDs matching `scripts/harvest_stacks.py`'s SHA-256 rule. **These source records are not certified canonical active candidates**.
- Recorded **109 source-scoped ledger entries** (chapter/section guards plus named definitions, notations, and Situation) and **52 after-section checkpoints**.
- **49 statements** contain explicit source `\\ref` dependencies (77 occurrences); 4 individual reference occurrences do not resolve within this chapter and require pinned cross-file lookups.
- The **named Situation `situation-inverse-limit-sites`** (§18, L3769 onward) is referenced by 4 candidates. In particular it specifies a cofiltered index category, finite index-set coverings, transition site morphisms, and composition compatibility. It must be expanded **only** for statements that actually invoke it.
- Sections containing no source result environments are still traversed for definitions and notation. The section contexts in the ledger are **lookup leads, not automatic theorem hypotheses**. Candidate-local quantified objects must not bleed into subsequent theorems.

## Gate and limits

**Stage A/A1 standalone-ready count: not established. Codex Stage B-ready count certified by this work: 0.** No source-first mathematical equivalence decisions have been made here. This A0 packet is *not* a replacement for a Chapter Stage A pass.

The registry files `harvest/active_candidate_ids.jsonl` and the full `harvest/phase2_calibration_2026-10-29/AUTHORITATIVE.jsonl` were too large to retrieve reliably through the available GitHub file interface. The smaller 68-record `APPROVED_OVERLAYS.jsonl` contained no `sites.tex` approvals, and the 16-entry duplicate alias crosswalk contained none, but this **does not prove** eligibility of all 161 source statements. Stage A must reconcile all records before creating a Stage B-ready manifest.

No old Stage A, Codex approvals, proof text, global further-work registry, or production corpus was modified.

## Cross-file/unknown-reference retrieval queue

- §5, L416, `lemma-almost-directed`: `\ref{categories-lemma-split-into-directed}`
- §5, L451, `lemma-directed`: `\ref{categories-definition-directed}`
- §29, L6981, `lemma-special-equivalence`: `\ref{sets-lemma-coverings-site}`
- §30, L7586, `lemma-relocalize-compare`: `\ref{equation-relocalize}`

## Artifacts and resumption

`MANIFEST.json` records counts and exclusions; `A0_WORKPACKETS_V2.jsonl` preserves original pinned source statement, source/candidate ID, structural cues and exact same-file reference targets; `CONTEXT_LEDGER.jsonl` contains source-introduction and noninheritance guards; `SECTION_CHECKPOINTS.jsonl` covers all sections.

**Next:** Resolve cross-file source refs, verify active/approved candidate IDs, then perform Stage A1 source-specific mathematical reconstruction for complete sections in order, without treating A0 cues as semantic validation. Only then set `reconstruction_completed_awaiting_independent_stage_b_validation` or an evidence-based `further_work_needed`.

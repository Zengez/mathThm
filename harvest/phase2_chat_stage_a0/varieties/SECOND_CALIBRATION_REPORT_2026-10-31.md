# Stage A0 v2: second Medium-style calibration — varieties §§3–12

> **AUDIT CORRECTION — INVALID NEW-WORK CALIBRATION (October 31, 2026).** The entire Varieties chapter had already been independently reviewed on October 29. Comparing the 64 experimental A0 work packets with `phase2_chapters_2026-10-29/varieties_a/INDEPENDENT_VALIDATION.jsonl`: **59 were already approved, two were previously held, and three were not canonical active candidates**. There were **zero eligible previously unreviewed candidates**; the two proposed substitutions applied only to noncanonical records. This run produced experimental extraction artifacts, not new Stage A0 progress on the pending workload. Read [the audit](SECOND_CALIBRATION_AUDIT_2026-10-31.md) before using these packets. Do **not** ingest them into Stage A readiness data.

**Date:** 2026-10-31  
**Working branch:** `work/phase2-stage-a-context-enrichment`  
**Pinned Stacks source:** `varieties.tex` at `a04446e57ec1fbc252a871afcec7752fb2807b14`  
**Source-order window:** §§1–12 walked, §§3–12 candidate-bearing; lines 17–2624.

This is a NEW source window, separate from the earlier `flat.tex` §§1–42 pilot. The window had no Chat Stage A manifest at selection time, but **that check was insufficient**: earlier independent review had already completed this entire chapter. The mistaken selection is documented in the audit linked above. The former "200 sections ahead" was an arbitrary overlap-avoidance estimate, **not** a precise offset requirement.

## Validated deliverables

| Measure | Count |
| --- | ---: |
| Candidate-bearing sections | **10** |
| Full physical sections accounted for (including two zero-candidate sections) | **12** |
| Source-derived candidate A0 work packets | **64** |
| Distinct candidate IDs | **64** |
| Source-literal declaration/premise fragments | **131** |
| Enumerated logical groups | **28** |
| Enumerated clauses/items preserved | **94** |
| Provisional literal setup/claim partitions | **41** |
| Source \ref occurrences identified | **15** |
| References resolved to earlier targets in pinned same chapter | **6** |
| Explicit source-backed safe preface suggestions | **2** |
| Context-ledger entries | **8** |
| After-section checkpoints | **12** |
| Candidate statements rewritten in authoritative data | **0** |
| Readiness/approval fields leaked into packets | **0** |

**Batch 1:** `batch_01_sections_03_07/`, 32 candidate overlays, five candidate-bearing sections plus two preceding context-only sections.  
**Batch 2:** `batch_02_sections_08_12/`, 32 candidate overlays in five candidate-bearing sections.

Each batch contains `MANIFEST.json`, `CONTEXT_LEDGER.jsonl`, `SECTION_CHECKPOINTS.jsonl`, `A0_WORKPACKETS_V2.jsonl`, and `REPORT.md`.

### Mechanical work done

- Preserved each candidate's exact source LaTeX, stable pinned candidate fingerprint, source label/line, chapter and section.
- Indexed the chapter notation `k` for ground field without assuming algebraic closure/characteristic; captured earlier definition environments separately from theorem hypotheses.
- Retrieved and attached matching same-chapter source environments for referenced labels; recorded unresolved or cross-chapter references as targeted A1 tasks.
- Gathered exact `Let`/`Assume`/`Set`/`Denote` source fragments, enumerated clauses, equivalence cues and safe-to-extract literal claim partitions. These are **not semantically verified hypotheses/conclusions**.
- Produced **two direct notation-inheritance prefaces** for `lemma-change-fields-algebraic-dim` and `lemma-change-fields-algebraic-unramified`, both referring to the setup of `lemma-change-fields-flat`. The prefaces copy the parent lemma's quantified field extension and base-change objects without importing its conclusions.
- Preserved A1 remaining work per candidate and did not promote anything to Codex or Stage B.

## Integrity and important limitations

The saved packets and both manifests parsed as valid JSON/JSONL, candidate counts matched manifests, **64/64 candidate IDs were unique**, 12 checkpoints were present, and no authoritative readiness fields appeared in the packets. The 68-record approved-overlay snapshot inspected during this run had **zero** overlaps with the new candidate IDs. A full 9,675-ID canonical active-pool membership check and the entirety of historical/new Codex approvals were **not** verified, so all 64 remain provisional A0 only.

The new packets contain substantially more per-candidate preparatory material than the initial `flat.tex` Medium run, which primarily supplied reference notes. Nevertheless, most of the 64 theorem statements were not rewritten; only two confidently sourced replacement prefaces were suggested. Whether this actually saves A1 effort needs subsequent High-thinking review, particularly on extracted condition lists, nested logical scopes, and assumptions inherited by reference.

**No theorem proofs were reviewed, no mathematical source-equivalence was certified, no Stage A or Stage B records were modified, and no full regression suite was run.**

**Next A0 source section if continuing in this chapter:** `varieties.tex` §13, line 2625.

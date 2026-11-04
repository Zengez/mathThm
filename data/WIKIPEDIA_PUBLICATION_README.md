# Published Wikipedia theorem corpus (2026-11-04)

**Status:** 920 new Wikipedia theorem/result records have been editorially prepared and have passed a **structural proof-presence** check. The results were added to the public mathThm catalog alongside the original 3,963 entries, for a total of **4,883** searchable theorem records.

## What the publication means

Each new record preserves the worker-prepared standalone statement, separate `hypotheses` and `conclusions`, a Wikipedia source article URL, and the **exact Wikipedia proof-section anchor** that passed a minimal presence-only check. Proofs have *not* been reviewed for correctness, rigor, completeness, validity, or theorem-statement correspondence. Record status is `cursory_screened_unverified`, with `mathematical_audit.status = not_audited`. Original source wording has not been represented as a verbatim transcription.

Canonical Wikipedia publication source: `data/wikipedia_theorems.jsonl`, containing exactly **920** stable `candidate.wikipedia.*` IDs. Its contents were generated once from:
- `work/wikipedia-proof-screen/20261104/proof_screened_candidates.jsonl` — original **706** passes
- `work/wikipedia-proof-screen/20261104/one-time-retry/newly_screened_candidates.jsonl` — **214** recovered passes

The existing **64** proof-section nonpasses, and the earlier **137** source-clarity holds, are intentionally excluded. The Stacks master `data/maththm_master.jsonl` retains its original **4,132** decisions and remains the authoritative Stacks source.

## Durable rebuild path

`scripts/publish_phase2_catalog.py --all` now combines:
1. The original 20 prototype records;
2. The 3,943 published authoritative Stacks records;
3. The 920 frozen Wikipedia publication records.

This rebuild is executed on each `Publish mathThm` GitHub Action run (including the nightly site rebuild), so the Wikipedia entries cannot disappear due to regeneration from only the Stacks master. No recurring Wikipedia crawling or proof screening was added.

The generated `data/theorems.json` and published `_site/theorems.json` contain all **4,883**. `work/phase2-final-publication/REPORT.json` now includes explicit Wikipedia counts while preserving all prior Stacks decision counts.

## Subject labels

Subject-area categories are assigned *conservatively* from explicit title/lead terms, and entries with no reliable keyword remain in the generic `Mathematics` group rather than being misleadingly classified. Subject area can be refined separately, without reopening the theorem/proof review.

Tests: `tests/test_wikipedia_publication.py` and the full structural/web regression suite. This publication is not a mathematical proof certification.

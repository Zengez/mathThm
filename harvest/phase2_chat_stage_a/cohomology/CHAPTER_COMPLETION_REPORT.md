# Cohomology chapter — Stage A completion report

Pinned source revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`  
Working branch: `work/phase2-stage-a-context-enrichment`  
Last section reviewed: §55 (end of `cohomology.tex`)

## Source-first Stage A disposition

- Total physical source sections accounted for: **55/55** across nine sequential batches.
- Active candidates inventoried: **231/231** (the original Pass 1 list has 243 entries, of which 231 are active).
- Prepared for independent Stage B: **215** (prior 195, new 20).
- Explicit further-work holds: **16** (prior 15, new 1).
- Previously approved candidates regenerated in this chapter: **0**.
- Stage B mathematical validation/proof checking in this chapter run: **none**; no Pass 3 promotion.

## New batch: §§51–55

| Section | Active | Ready for Stage B | Further work |
|---|---:|---:|---:|
| §51: Miscellany | 4 | 4 | 0 |
| §52: Invertible objects in the derived category | 2 | 2 | 0 |
| §53: Compact objects | 2 | 2 | 0 |
| §54: Projection formula | 4 | 4 | 0 |
| §55: An operator introduced by Berthelot and Ogus | 9 | 8 | 1 |

The final 21 source statements were read directly from the pinned Stacks text. The context ledger carries only legitimate definitions and named context. In §54, the earlier defined projection-formula natural transformation is included explicitly in later statements. In §55, Situation eta is expanded to the locally regular-generator condition, the η construction and Bockstein complex are located at their source introductions, and the Situation expires at the chapter boundary.

**New hold:** `candidate.stacks.4f39c963510145d8d90cddfa`, `lemma-eta-qis`, §55 L14257. The original asserts the η-induced map is a quasi-isomorphism “too” without an explicit assumption that the input map is a quasi-isomorphism. This missing hypothesis requires adjudication, rather than a silent editorial correction. See `harvest/phase2_chat_stage_a/cohomology/batch_09_sections_51_55/RECONSTRUCTIONS.jsonl` and global `FURTHER_WORK_NEEDED.jsonl`.

## Local consistency checks

Confirmed by generation-time assertions: 21 unique candidate IDs, all active; zero overlaps with existing authoritative approval files; pinned source locators; contiguous sections and §50 checkpoint; 21 candidate decisions equal 20 ready plus one held; global hold registered; manifest counts and per-section ready/hold tallies consistent; no source or proof files altered. **Full repository regression tests and independent Stage B proof/semantic validation were not run.**

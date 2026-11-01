# Stage A — third regular source-first pass (90 sections, six 15-section batches)

Date: October 31, 2026  
Repository: `Zengez/mathThm`  
Branch: `work/phase2-stage-a-context-enrichment`  
Pinned Stacks revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`  
Last processing commit: `eb5bb14d8f975677f95797ff11de00482f03b43d`

## Completed source-order scope

This pass started at `spaces.tex` §14 (L2161), immediately after the previous 60-section pass. Six consecutive groups of exactly 15 source sections were reviewed, including all context-only and no-active-candidate sections. The source-first context ledger was carried across the processing batches and chapter-local state was discarded at each chapter exit.

| Processing batch | Sections reviewed, in pinned order | Candidate records | Standalone prepared for Stage B | Further work needed | Commit |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | `spaces.tex` §§14–16; `spaces-properties.tex` §§1–12 | 35 | 33 | 2 | `0188ad46347b4f522d1eb8ac47f3d5d645ac3a93` |
| 2 | `spaces-properties.tex` §§13–27 | 51 | 42 | 9 | `6fb3d04ecda4cff4496e3c73e3efd164916f965b` |
| 3 | `spaces-properties.tex` §§28–34; `spaces-morphisms.tex` §§1–8 | 46 | 41 | 5 | `62e305180a2680592b603f8550ea88494da45ec2` |
| 4 | `spaces-morphisms.tex` §§9–23 | 71 | 69 | 2 | `cf97abc67449300e0b0393abaf4f38c677f5c138` |
| 5 | `spaces-morphisms.tex` §§24–38 | 87 | 85 | 2 | `766c86d519cb3f1aa742012fef70325fa31cf443` |
| 6 | `spaces-morphisms.tex` §§39–53 | 51 | 49 | 2 | `f57274b816d50553f78f56c8b76164030e9273e1` |
| **Total** | **90 sections** | **341** | **319** | **22** | |

Chapter totals: `spaces.tex` §§14–16: 3 sections / 7 candidates (5 ready, 2 held); `spaces-properties.tex` §§1–34: 34 sections / 94 candidates (80 ready, 14 held); `spaces-morphisms.tex` §§1–53: 53 sections / 240 candidates (234 ready, 6 held).

These are **Stage A preparation decisions**, not independent Stage B mathematical approvals. Existing source objects, original theorem text, candidate IDs and historical Phase 2 approval records were left unchanged. The full pre-existing mathematical-approval registry was checked for overlapping IDs in these three source chapters; none were found.

## Working files

New preparation records were committed in the existing seven batch folders:

- `harvest/phase2_chat_stage_a/spaces/batch_02_sections_04_16/`
- `harvest/phase2_chat_stage_a/spaces-properties/batch_01_sections_01_07/`
- `harvest/phase2_chat_stage_a/spaces-properties/batch_02_sections_08_27/`
- `harvest/phase2_chat_stage_a/spaces-properties/batch_03_sections_28_34/`
- `harvest/phase2_chat_stage_a/spaces-morphisms/batch_01_sections_01_13/`
- `harvest/phase2_chat_stage_a/spaces-morphisms/batch_02_sections_14_33/`
- `harvest/phase2_chat_stage_a/spaces-morphisms/batch_03_sections_34_53/`

Within each folder the updated `MANIFEST.json` and `RECONSTRUCTIONS.jsonl` correspond to its source sections; `CONTEXT_LEDGER.jsonl` and `SECTION_CHECKPOINTS.jsonl` record source definitions, section scopes, noninheritance guards and resume markers. Chapter-inherited conventions were explicitly scoped and did not automatically add hypotheses to later lemmas. This includes the global big-fppf-site and base conventions, scheme/algebraic-space distinctions, exact vs. geometric-stalk conditions, and scheme-valuative vs. algebraic-space-valuative existence.

The final five sections of `spaces-morphisms.tex` (§§49–53) had **zero active candidates**, yet were traversed and checkpointed. In particular §49's normalization definition and §53's universal-homeomorphism definition were recorded as context; no candidate output was invented. At the end of §53, the chapter scope stack was reset.

## Source ambiguity and holds

Every held candidate has its source line, a concrete issue, packet path, and `status=further_work_needed` in the central registry:

`harvest/phase2_chat_stage_a/FURTHER_WORK_NEEDED.jsonl`

Representative examples include:

- `spaces.tex` §14 group-action quotient: site-size of a possibly infinite disjoint union; §15 essential-image criterion for enlarging a big site.
- `spaces-properties.tex` §18 comparisons of small étale sites and topoi; §19 “geometric points of S” occurring in a claim about sheaves on X; §20 support of a section over U described as closed in |X|; §28 locally ringed-topos 2-morphism/full-faithfulness; §34 quotient by an arbitrary abstract group.
- `spaces-morphisms.tex` §13 `lemma-stalk-push-closed` appears to reverse sheaf-stalk indices; §22 germ-property Q is defined through an external Descent result; §30 `lemma-fpqc-quotient-topology` uses ambiguous `|T|` for T already a subset of |Y|, and `lemma-flat-morphism-sites` requires a precise flat ringed-site definition; §§41–42 a valuation-ring lift/compound refined valuative criterion requires further diagram and quantifier adjudication.

In §41 the source specifically permits the field extension `K'/K` and a dominating valuation ring `A'` in the **existence** half of the valuative criterion. The **uniqueness** half is the ordinary unextended uniqueness test. These distinctions were retained; the two technically ambiguous valuation claims remained on hold rather than being treated as the usual scheme criterion.

The central further-work registry contained **294 entries** after this run, of which **22** refer to the newly processed 90 sections.

## Repository validation actually run

All seven affected packet folders were reread from the branch after the final processing commit. The following checks passed:

- All **341 candidate IDs are unique**; candidate source files and source revisions match the pinned source.
- The 341 records are split into exactly **319** `reconstruction_completed_awaiting_independent_stage_b_validation` and **22** `further_work_needed`, with **zero** legacy pending records in the selected scope.
- No ready record has nonempty `stage_a_remaining_work`; every held record specifies an unresolved issue and appears in the central further-work registry.
- No processed record was marked `proof_reviewed=true`, `phase3_eligible=true`, or `published=true`.
- Exactly **90/90 selected source sections** have one matching source-revision-matched and complete section checkpoint, and one manifest entry marked source-context-reviewed.
- Checked ledger files contain **111 unique source-anchored context-event IDs** in the seven touched folders (some context events existed before the beginning of this run). No entry typed `definition` is marked as a standing assumption.
- The final checkpoint after `spaces-morphisms.tex` §53 records empty chapter-local scope and the next pinned locator.

Files were validated as JSON/JSONL when written and after readback. No local `pytest` or end-to-end repository regression suite, proof checking, independent mathematical equivalence audit, or Codex Stage B job was run during this preparation pass.

## Exact resume frontier

**Next regular Stage A source-order section:** `decent-spaces.tex`, **§1**, source line **17** (“Introduction”) at the pinned Stacks revision.

The last resume checkpoint is in:

`harvest/phase2_chat_stage_a/spaces-morphisms/batch_03_sections_34_53/SECTION_CHECKPOINTS.jsonl`

Refresh GitHub head and any other concurrently updated preparation/approval records before the next run. Continue whole sections and maintain source-anchored chronological context across every intervening section; do not import previous chapter hypotheses unless explicitly inherited and justified.

No user decision is required before continuing. Stage B equivalence validation remains independent and pending for the Stage A-ready candidates.

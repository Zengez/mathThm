# mathThm harvesting — minimal three-pass runbook

**Status: October 28, 2026.** A lightweight, bounded Python toolkit exists. It is NOT a mathematical proof checker or autonomous research engine. No raw candidates or questionable cases are published automatically. See HARVEST_DESIGN.md and THEOREM_RECORD_CONTRACT.md.

## CURRENT CAMPAIGN OVERRIDE — prototype population and Pass 3

The initial Pass 2 bulk-discovery campaign is closed for the prototype. **Only the 9,675 canonical candidate IDs in [harvest/active_candidate_ids.jsonl](harvest/active_candidate_ids.jsonl) are considered active.** The separate [active-pool manifest](harvest/ACTIVE_CANDIDATE_POOL.json) records the current recognized intake and batch membership. The historical Pass 1/2 files intentionally retain all original sources; they are NOT active-pool counts.

The deferred cases live exclusively for future discovery in [harvest/problem_candidates.jsonl](harvest/problem_candidates.jsonl) with difficulty groups and a [manifest](harvest/PROBLEM_CANDIDATES_MANIFEST.json). Pass 3 packets, manual Pass 3 decisions and staging ignore those IDs; routine status reports track only active intake. If a new separate research phase chooses to revisit these cases, start it deliberately and rebuild the pool only after accepted canonical decisions change.

**Current gating decision:** Do not begin Pass 3 proof screening of this Stacks campaign merely because a candidate was marked Pass 2 resolved. Every candidate needs standalone-source-context validation first, and the eight provisional duplicate mergers need another mathematical-context comparison. The following Pass 3 commands are retained for use **after** the standalone gate is met; they are not the current next action:

```bash
python -m scripts.active_candidate_pool
python -m scripts.harvest_pipeline pass3-packets --workdir harvest/batches/stacks-bulk-2026-10-28 --source-root /path/to/pinned-stacks-source
python -m scripts.harvest_pipeline status --workdir harvest/batches/stacks-bulk-2026-10-28
```

Repeat Pass 3 for the other active Stacks batches. The pinned upstream source must be present for nontruncated proof excerpts. This transition does not read, screen, or publish any theorem proof.

---

## CURRENT SCALE EXPERIMENT — 300 consecutive candidates across adjacent chapters

The [latest 300-candidate source-context reconstruction](harvest/section_walk_scale300_2026-10-28/REPORT.md) spans **54 complete consecutive sections**, not a selected collection of disconnected sections. The source pair is **coherent.tex, chapter 30, lines 2923–8138**, followed immediately by **divisors.tex, chapter 31, lines 17–9492**, including the chapter's zero-candidate Introduction. No single remaining uninterrupted chapter-local span was long enough to reach the user's requested 270–330 candidate window.

**Outcome:** 300 independent draft overlays saved: **242 structurally draft-ready for separate mathematical equivalence validation and 58 on explicit source/context/logical-scope holds**. None is proof-verified, finally source-equivalence approved, Pass 3 eligible or published. Original Pass 1/2 and 9,675-member intake remain unchanged. The [cross-batch registry](harvest/SECTION_WALK_COMPLETED_SECTIONS.json) tracks **80 completely drafted sections and 554 candidate drafts** across the 30, 74, 150 and 300 candidate pilots. It must be consulted before selecting new source sections.

**Practical commands**, when using the pinned Stacks source checkout and the saved source-selection manifest:

```bash
python -m scripts.stacks_cross_chapter_section_window300
python -m scripts.stacks_section_walk_scale300
python -m scripts.stacks_scale300_context_passages
python -m scripts.stacks_section_walk_scale300_reconstruct
python -m scripts.validate_stacks_section_walk_scale300
python -m unittest discover -s tests -q
```

These stages are explicitly distinct: adjacent-chapter selection, pinned source traversal, limited section/source context collection, theorem-specific draft creation with contextual holds, then structural and scope validation. The actions reproduce them without reading proof bodies. Source-level definitions `Coh(X,I)` and norms of degree `d` were recorded as term meanings, not inherited hypotheses; other named definitions retain chronological source scope. Chapter-specific conventions reset at the physical chapter boundary.

**Important regression gate:** A theorem with `Assume \begin{enumerate} ... \end{enumerate} Then ...` has the list as **premises**, not conclusions. Equivalence conditions are not hypotheses; clauses with a joint existential witness must remain grouped. Tests in `tests/test_stacks_scale300_logic.py` and the batch validator guard against these errors. The 58 held cases are documented per-candidate (not lost); 43 have source-reference expansion needs, with overlapping nested enumeration and existential logic issues. Do not mistake draft-ready for verified mathematical equivalence.

---

## CURRENT METHOD: consecutive full-section standalone reconstruction (latest 150)

The agreed source-context reconstruction unit is a **whole source section**, processed along with its neighboring sections in physical source order. To measure scaling, select a run containing approximately the requested candidate count but **never cut through a section**; include intervening sections even if they have zero active candidates.

The latest run is [150 active candidates across 19 consecutive `algebra.tex` sections](harvest/section_walk_scale150_2026-10-28/REPORT.md), lines 4284–10036. It contains **134 editorial standalone drafts ready for final source-equivalence checking, 16 held for mathematical/contextual issues, and 0 approved Pass 3 proofs**. [Checkpoints](harvest/section_walk_scale150_2026-10-28/SECTION_CHECKPOINTS.jsonl) record all 19 complete sections, including a zero-active section, and keep only definitions and context still in valid scope. The original Pass 1/2 data and active-pool IDs were untouched.

**Scope rules:** A section and its named definition environments contribute term meanings, not automatically theorem hypotheses. Temporary assumptions of a lemma/proposition are popped when that environment ends. An explicit chapter/section convention persists only within its justified scope. The two source prose signals in this run were adjudicated (not auto-inherited) in [SCOPES_REVIEWED.json](harvest/section_walk_scale150_2026-10-28/SCOPES_REVIEWED.json). Definitions enter only on or after their original source line; *normal domain* and *normal ring* have different definitions and must not be conflated. All proof environments are omitted during this stage.

**Actual executable machinery** (pinned Stacks source checkout required for source traversal):

```bash
python -m scripts.stacks_consecutive_section_window150
python -m scripts.stacks_section_walk_scale150
python -m scripts.stacks_scale150_context_passages
python -m scripts.stacks_section_walk_scale150_reconstruct
python -m scripts.validate_stacks_section_walk_scale150
python -m unittest discover -s tests -q
```

The first command produces candidate windows from *physically consecutive* complete sections and excludes previously processed sections. For future batch sizes, adapt the selected window and manifest rather than relying on exactly 150 or choosing separate high-density sections. The next scripts produce source-order event packets, review only encountered local definitions, create source-faithful standalone statements and record uncertainty, then validate context expiration, complete-section boundaries, candidate IDs, and regressions.

**Quality gate:** A `standalone_draft_ready_for_validation` flag is an editorial draft status **not** a final mathematical source-equivalence certificate. Mathematical statements with enumerated alternatives must preserve the correct logical form: the alternatives are *conclusions* of an equivalence, not global hypotheses; separately guarded implications keep their guards; and multiple properties of one existential witness stay grouped. This was explicitly corrected in the scale-150 code. The final semantic verification and all theorem proofs remain separate tasks, and no draft is automatically promoted to the public catalog.

---

## SOURCE-CONTEXT RECONNAISSANCE — before standalone Pass 2 validation

Before Pass 3, make the canonical theorem hypotheses/conclusions self-contained relative to unambiguous mathematical terminology. Use the lightweight Stacks scan at [harvest/stacks_context_recon_2026-10-28_priority.md](harvest/stacks_context_recon_2026-10-28_priority.md), [per-file source-line leads](harvest/stacks_context_recon_2026-10-28_files.jsonl) and the [scan manifest](harvest/stacks_context_recon_2026-10-28_manifest.json).

This is a **high-recall lead scan only**, not parsed standing context. The pinned source's maintained Makefile provides chapter ordering; source section headings and broad phrase matches flag possible conventions. A chapter occurring earlier does **not** make its assumptions applicable later. Review true scope before promoting anything to theorem hypotheses, and distinguish source definitions, standing assumptions and facts used only in proofs. Check provisional duplicate mergers again after standalone expansion.

Rebuild the source-line lead scan (requires the pinned Stacks checkout):

```bash
python -m scripts.stacks_context_recon --source-root upstream/stacks --output-dir harvest
```

Deliberately stop at global/chapter conventions, short section introductions, and a basic label lookup; resolve additional local dependencies per-candidate rather than constructing a large universal context graph.

### First bounded conventions review — complete

The [reviewed standing-context atlas](harvest/stacks_standing_context_atlas_2026-10-28.jsonl) now contains **55** designated convention/notation/setup source-section reviews from **48** chapters. The companion [chapter lookup](harvest/stacks_standing_context_lookup_2026-10-28.json) covers all **115** maintained chapters and records **21** explicitly documented inheritance/reference links without recursively resolving them. A [short explanatory summary](harvest/stacks_standing_context_summary_2026-10-28.md) records useful repeated-context families and noninheritance/override safeguards; [source review packets](harvest/stacks_context_sections_2026-10-28_packets.jsonl) preserve pinned-source excerpts and links.

These are **source-context leads**, not assertions already imported into any theorem hypotheses. Read each section's `scope_assessment`, `candidate_action`, `guards` and `inherit_context_ids` before using it. A headline such as "Conventions" does not prove that every listed fact applies globally; a phrase "we will often assume" does not establish an assumption for an individual theorem. The formal-spaces new convention starts only at the marked section line; Chow chapter Situation setups must be checked for applicability; moduli base conventions may override the inherited setting.

To rebuild the reference from the committed review annotations (without source browsing or proof reading):

```bash
python -m scripts.stacks_context_index
```

Example read-only retrieval from a candidate's pinned filename and source line:

```python
from scripts.stacks_context_index import get_candidate_context_leads
leads = get_candidate_context_leads("formal-spaces.tex", statement_line=900)
```

This retrieves global/chapter convention *leads only*. The next lightweight step is to index chapter/section opening paragraphs and exact source labels; deeper contextual resolution remains per-candidate, and Pass 3 remains blocked until standalone semantics are checked.

---

## LIGHTWEIGHT CONTEXT LOOKUPS AND FIRST PILOT — completed

The indexed pinned source has **115 chapters**, **3,288 section openings**, and **21,297 exact source labels with no collisions**. No mathematical assertions were inferred. See [section-opening preview index](harvest/stacks_context_openings_2026-10-28.jsonl), [exact source-label locator](harvest/stacks_context_labels_2026-10-28.json), and [index summary](harvest/stacks_context_light_index_summary_2026-10-28.md).

For a candidate with a filename, source line number, and optional `detected_local_references`, retrieve the source and standing-convention *leads* in one operation:

```python
from scripts.stacks_context_light_index import candidate_context_bundle
packet = candidate_context_bundle("moduli.tex", 409, ["situation-numerical"])
```

The lookup chooses the source section by physical file/line and resolves references **only** by an exact same-chapter short label or an exact, chapter-qualified full label. It does not read proof bodies, follow reference chains, auto-propagate chapter assumptions, or create new theorem hypotheses. Any excerpt truncated at the index's 1,800-character cap may be fetched from the same pinned Stacks source if relevant.

The [19-candidate context pilot](harvest/standalone_context_pilot_2026-10-28_summary.md), [packets](harvest/standalone_context_pilot_2026-10-28_packets.jsonl), and [first-pass editorial notes](harvest/standalone_context_pilot_2026-10-28_first_review.jsonl) document 11 candidate-specific screens and 8 merger-context comparisons. **14/14 explicit labels in the pilot resolved exactly**; six candidates have preliminary expanded hypothesis language, but none has passed final standalone validation. This pilot shows that a named Situation copied by Pass 2 can still leave local assumptions or notation unresolved—for example, the missing separated/finitely presented morphism assumption stated in Moduli's section introduction.

**Next step:** Stop adding meta-index infrastructure. Process standalone candidates in bounded batches, recording explicit hypotheses, conclusions, source pointers, unresolved local terminology, and the outcome of candidate-specific scope checks. Do not spend extensive effort chasing a single difficult reference; mark it for later. Only after standalone review should the provisional source-duplicate mergers be re-adjudicated and Pass 3 resume.

---

## What each pass does

1. **Pass 1:** Scripts scan explicitly selected Stacks Project LaTeX chapter files for theorem/lemma/proposition/corollary environments followed by an apparent proof environment. They capture complete source statements, pinned source revision, source URL, exact source line, proof location and source confidence. They **do not read or assess the proof**. Pass 1 false positives are acceptable.
2. **Pass 2:** A statement-structuring packet is created from each raw candidate. Up to two local same-file referenced theorem statements may be supplied as context, without chasing further dependencies. A human or model reviewer adds the faithful displayed restatement, hypotheses, conclusions and initial tags. Unresolved context becomes needs_context.
3. **Pass 3:** A bounded proof excerpt is prepared from the original source; a human/model reviewer scans it and submits a verdict. Plausible means a full quick scan saw no obvious issue; questionable means a strict stop was reached; rejected requires an identifiable issue. Truncated packets cannot become plausible without an explicit assertion that a complete scan was actually done elsewhere. **The scripts never assign a mathematical verdict.**

Questionable, rejected and needs_context items remain in a separate needs_more_investigation.jsonl file with their source/proof URLs. Rejection of a cited proof does NOT assert that the theorem itself is false. Source confidence and proof-screening confidence stay distinct.

## Files and tools

- scripts/harvest_stacks.py — bounded, source-native Pass 1 extraction; pinned revisions; idempotent candidate IDs.
- scripts/harvest_pipeline.py — Pass 2/3 review packets and decisions, investigation queue, restart checkpoint, explicit staged promotion.
- .github/workflows/harvest-stacks.yml — manual GitHub Action for ONE selected Stacks chapter (limit 1–500), producing downloadable raw candidate artifacts only.
- tests/test_harvest_pipeline.py — offline end-to-end tests.
- data/theorems.json — current published catalog, never modified by Pass 1/2/3.
- .harvest_runs — recommended local workspace, not part of the public site.

## Option A: Start a Pass 1 in GitHub

Visit https://github.com/Zengez/mathThm/actions/workflows/harvest-stacks.yml and select Run workflow. The default chapter is categories.tex, default maximum is 100. The workflow fetches a pinned snapshot of that single public Stacks source chapter, runs mechanical Pass 1, and uploads a stacks-raw-candidates artifact containing pass1.jsonl and checkpoint.json. Download/unpack that artifact into a local workspace to continue. It does **not** push to the repo or publish a theorem. Its source strategy does not depend on Stacks's less-stable public API.

## Option B: Start Pass 1 locally

Clone/check out the Stacks Project at a known full 40-hex-digit commit SHA. Replace SOURCE_COMMIT below with that actual SHA:

    python scripts/harvest_stacks.py --source-root /local/stacks-project --source-ref SOURCE_COMMIT --files /local/stacks-project/categories.tex --batch-id stacks-categories-001 --max-candidates-per-file 100 --output-dir .harvest_runs/stacks-categories-001

For source fidelity, the raw candidate file stores full original LaTeX statement text, not a source-derived paraphrase. The accepted website uses separately reviewed faithful statements and preserves attribution. Stacks material is under the GNU Free Documentation License; review reuse requirements before publicly reproducing substantial original language.

## Pass 2 commands

    python scripts/harvest_pipeline.py pass2-packets --workdir .harvest_runs/stacks-categories-001 --source-root /local/stacks-project

This writes pass2_packets.jsonl. A reviewer/model creates a JSONL file where each line is one object of this shape:

    {"candidate_id":"candidate.stacks.REPLACE_WITH_ACTUAL_ID","context_status":"resolved","statement":"If $f$ is continuous on a compact space $X$, its image is compact.","hypotheses":["$X$ is compact","$f$ is continuous"],"conclusions":["The image of $f$ is compact"],"hypothesis_tags":["compactness","continuity"],"conclusion_tags":["compactness"],"area":"Topology","title":"Compact image","context_note":""}

This is an EXAMPLE, not an extraction from a specific source. For unresolved local assumptions, set context_status to needs_context and supply a nonempty context_note rather than inventing hypotheses/conclusions.

    python scripts/harvest_pipeline.py pass2-apply --workdir .harvest_runs/stacks-categories-001 --decisions pass2-decisions.jsonl

## Pass 3 commands

    python scripts/harvest_pipeline.py pass3-packets --workdir .harvest_runs/stacks-categories-001 --source-root /local/stacks-project --max-proof-chars 7500

This writes pass3_packets.jsonl for resolved candidates only. A human/model reads the provided proof or visits its cited URL, without substantial extra research. Reviewer decision example:

    {"candidate_id":"candidate.stacks.REPLACE_WITH_ACTUAL_ID","outcome":"questionable","scan_completed":false,"reason":"Proof references another argument whose validity would require substantial background; stop rule reached","proof_checked_on":"2026-10-28"}

For plausible, require scan_completed=true. For rejected, require a positive identifiable issue in reason. A proof excerpt marked truncated cannot be promoted as plausible unless a reviewer actually scans the full proof at its source and explicitly states full_proof_reviewed_externally=true. If no ending proof marker was found, manually_verified_proof_completion=true requires actual evidence that the proof appears finished, not guesswork.

    python scripts/harvest_pipeline.py pass3-apply --workdir .harvest_runs/stacks-categories-001 --decisions pass3-decisions.jsonl

## Investigation queue and staging

    python scripts/harvest_pipeline.py status --workdir .harvest_runs/stacks-categories-001

The checkpoint is regenerated from the actual stage files; decisions and raw candidates persist independently. needs_more_investigation.jsonl holds all questionable/rejected and context-blocked entries with reasons and provenance. No mathematical validity implication is made by a Pass 3 verdict.

Only fully structured, explicitly plausible candidates can enter a staged catalog:

    python scripts/harvest_pipeline.py promote --workdir .harvest_runs/stacks-categories-001 --catalog data/theorems.json --output .harvest_runs/stacks-categories-001/staged-theorems.json

This validates the accepted schema. It does **not** modify data/theorems.json, git, GitHub Pages or mathDef. A later explicit review and commit of a staged catalog is required for public publication. Rerunning steps is idempotent, and conflicting decisions require explicit --replace rather than overwriting evidence silently.

## Resource limits and next phase

Keep the first run source-driven and simple: one or a few files, bounded 25–100 candidate batches, no dependency graph, no recursive math research, no multiple-proof classification, no semantic duplicate reconciliation. The initial target remains at least 200–300 provisionally accepted theorems before reevaluating website search/performance design. The tools support human or model reviewers, but don't themselves run an LLM or claim to verify logic.

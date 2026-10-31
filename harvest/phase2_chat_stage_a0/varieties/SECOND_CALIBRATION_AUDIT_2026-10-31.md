# Independent audit: second Stage A0 calibration, varieties.tex §§3–12

**Audit date:** October 31, 2026  
**Branch:** `work/phase2-stage-a-context-enrichment`  
**Source revision:** `a04446e57ec1fbc252a871afcec7752fb2807b14`  
**Verdict:** **INVALID AS A TEST OF A0 ON UNPROCESSED CANDIDATES**; useful as a limited structural-extraction demonstration. Do not count its packets as new Stage A progress.

## Critical selection error: entire Varieties chapter was previously independently reviewed

The original second-calibration report checked only `harvest/phase2_authoritative_2026-10-29/APPROVED_OVERLAYS.jsonl` (68 records). That is **not** the complete authoritative approval registry. The repository's `harvest/PHASE2_AUTHORITATIVE_REGISTRY.json` points to that file **and** `harvest/phase2_calibration_2026-10-29/AUTHORITATIVE.jsonl`, while the chapter's independent review is recorded under `harvest/phase2_chapters_2026-10-29/varieties_a/`.

`harvest/phase2_chapters_2026-10-29/REPORT.md` says the entire Varieties chapter had already been independently reviewed on October 29: **237 active canonical candidates across all 48 sections, 232 approved and five held**. The A0 trial's ten candidate-bearing sections are a subset of those sections and are **not untouched** just because no `harvest/phase2_chat_stage_a/varieties/` manifest exists.

Comparing every one of the A0 trial's 64 candidate IDs against `varieties_a/INDEPENDENT_VALIDATION.jsonl` gives:

| Existing prior status | A0 packets |
| --- | ---: |
| `source_equivalence_approved` | **59** |
| `context_resolution_required` | **2** |
| Not among the 61 canonical active candidates in those sections | **3** |
| **Total** | **64** |

The two prior holds are `theorem-varieties-rational-maps` (source category-variance issue) and `lemma-geometrically-irreducible-local` (empty-scheme criterion issue). The three **noncanonical** extra A0 overlays are `lemma-change-fields-algebraic-dim` (line 283), `lemma-change-fields-algebraic-unramified` (line 299), and `lemma-geometrically-reduced-any-base-change` (line 524). The last contains a literal source list item `Add more here.`, an additional reason not to treat every theorem-like source environment as active.

**Crucially, both of the A0 trial's proposed source-backed prefaces were for the first two noncanonical overlays**, not for any of the 61 active candidates. These proposals were non-authoritative and did not alter their statements.

The actual active-pool counts from `VARIETIES_COVERAGE.json` for §§3–12 are **61**, not 64 source-looking environments. The original 64-count is a mechanically generated overlay count and must never be reported as 64 new active-candidate preparations.

## What was technically produced and verified

The two A0 packets contain the exact pinned original source text for all 61 prior canonical candidates, matching `varieties_a/RECONSTRUCTIONS.jsonl` **byte-for-byte for their original statements**. Across all 64 generated overlays:

- 64 distinct IDs and valid JSON/JSONL; 12 post-section checkpoints including the two zero-candidate introductory sections
- 131 source-literal declaration or premise cue *fragments*, **not 131 verified premise clauses**
- 28 `enumerate` groups, 94 extracted numbered items
- 41 provisional source-text setup/claim partitions
- 15 `\\ref` occurrences across 14 candidates, six with prior same-file targets
- nine **unresolved cross-chapter** or other nonlocal references, even though the pinned source-label index exists
- two provisional preface substitutions, both for noncanonical extra candidates
- zero edits to authoritative A1/Stage B records and zero claimed proof reviews

Those are credible *extraction counts*, but are **not** measures of substantive, completed mathematical preparation on work waiting for A1.

## Representative source-first quality findings

1. **Useful simple structure:** `lemma-product-varieties` (line 85) has its algebraically closed field, two varieties and “Then” split exposed; `lemma-birational-varieties` (line 205) records one object declaration and all four equivalence clauses. This could spare superficial A1 transcription.
2. **Missed easy implication handling:** `lemma-change-fields-flat` (line 237) has “If (y) lies over (x), then” followed by four assertions. A0 marked its four-clause list `unclassified_list` and did not segment the visible antecedent and conclusions. A source fragment runs through the `Then` and into the conclusions.
3. **Missed independent conditionals:** `lemma-perfect-reduced` (line 400) contains two separate conditional claims; A0 made no hypothesis/conclusion partition and gave no two-claim structure. Prior A1 correctly distinguished local and global guarded conclusions. This is an achievable Medium-level prep task, without solving any mathematical theorem.
4. **Complicated but still mechanically analyzable:** `lemma-galois-action-connected-components-continuous` (line 1283) has an assumption list, an asserted conclusion list and a separate “Moreover” sufficient condition. A0 extracted two enumerations but left the second unclassified; it did not prepare the final independent-conditional structure.
5. **Multiple separately guarded results:** `lemma-proper-geometrically-reduced-global-sections` (line 1932) has eight conjunctive assertions, several individually conditional; A0 put all eight in an `unclassified_list`, without preserving the guard for each as a structured source clause.
6. **Previously recognized hard holds not reused:** The source-variance issue for `theorem-varieties-rational-maps` (line 164) and empty-scheme issue for `lemma-geometrically-irreducible-local` (line 1404) were in the prior independent validation, but A0 re-issued generic unverified tasks rather than carrying their existing adjudication. Medium need not settle these issues, but it should not make A1 rediscover them.
7. **Source reference lookup unfinished:** Nine `\\ref` references remain nonlocal, including routine `algebra-definition-geometrically-reduced` and `morphisms-definition-smooth` label lookups. These should be resolved to exact pinned definitions at A0 when inexpensive; a clear external-lookup hold is appropriate only if resolution is not available.
8. **Coverage/maturity:** Of 61 canonical candidates, 21 did not receive even a provisional setup/claim partition. Some are genuinely complex, but others have plainly visible `If...then` or an ordinary declarative conclusion. The A0 packets do not have independently usable source-literal `hypotheses` and `conclusions` fields.
9. **No ledger leak detected:** The chapter statement that (k) denotes the ground field was recorded as notation, not an assumption that (k) is algebraically closed. The seven source definition events and 12 checkpoints are useful bookkeeping, but a ledger's empty scope stack is not a substitute for a source-specific applicability review.

The earlier approved reconstruction records contain `correction_applied:true` for many of the matching candidates, but that flag includes contextual materialization and repackaging, **not necessarily mathematical mistakes**; it should not be used as an error-rate proxy.

## Operational changes needed before another calibration

1. **Eligibility first, before source scraping or selecting sections.** Read `PHASE2_AUTHORITATIVE_REGISTRY.json`, both authorized approval overlay families, chapter-level independent validation/coverage, and candidate-ID active-pool registry (or already validated chapter membership). Exclude *both* previously approved and previously held/reviewed candidates from a fresh A0 calibration. A section lacking a Chat Stage A manifest is not necessarily unprocessed. Abort and select a different window if the eligible count is zero.
2. **Separate three populations in manifests:** all source theorem-like environments, active canonical candidates, and eligible unprocessed A0 target candidates. Count only the third for a new-run workload metric. Check the source candidate ID against the canonical active pool before writing candidate work packets.
3. **Improve visible logical extraction:** Split exact source-local declarations from source-local assumptions and result clauses; correctly handle `If...then`, multiple independent conditions, `Then`-introduced enumeration assertions, `Moreover` clauses and condition-specific guards. Preserve the original LaTeX verbatim; add a structured *source-literal* hypothesis/conclusion skeleton even where it is not safely standalone.
4. **Finish routine reference discovery:** Resolve external source labels via the pinned label index, and collect useful adjacent definition/Situation text. Keep named definitions out of the hypothesis list unless the statement actually imports their assumptions. Reuse existing precise prior holds as read-only context if present.
5. **Audit cost/benefit on genuinely untouched candidates:** A0 does not need to approve any theorems. Score it instead on completed low-inference subtasks per eligible candidate and A1 source lookup/transcription work avoided. The A0 packet pass was largely pattern-driven extraction, not 64 individual mathematically reasoned Medium reviews; the present experiment cannot establish the intended High-thinking savings.

**Source-integrity check:** All reviewed A0 packet files and the existing independently validated Varieties records remained unmodified by this audit. These experimental work packets must not be ingested or promoted. The current selection mistake caused duplicated *experimental notes*, not changes to the existing approved theorem data.

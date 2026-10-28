# mathThm theorem record contract — revision 2

**Adopted October 28, 2026.** This is the data contract used by the now-implemented lightweight harvesting scripts in HARVEST_RUNBOOK.md; it is **not** a mathematical proof-verification contract. The catalog retains the outer schema name maththm.theorems.v1 so the existing website remains compatible, and sets contract_revision to 2.

## Guiding rules

**Fast intake:** A theorem may enter the public catalog only after an actual, accessible proof was opened and inspected enough to determine that it appears to claim completion. This is not a mathematical validity audit. Unread proof citations remain in an eventual separate candidate queue. Multiple methods, theorem dependencies, detailed equivalence auditing and sophisticated source discovery are explicitly deferred.

**Statement fidelity:** Store a mathematically faithful unified statement in the existing statement field, preserving original wording where legally possible and useful. Record source URL, statement locator, and structured editing provenance. Never fabricate an original quote. If exact source text was not retained, state that explicitly with a null value. Do not blindly construct a theorem from separate hypotheses/conclusions because that could change quantifier scope.

**Keep statuses separate:** Acquisition status tracks only superficially completed proof accessibility. Mathematical-audit status tracks later proof correctness. The prototype's legacy review_status stays cursory_screened_unverified until the UI supports audited records.

**Keep definitions separate:** mathDef V2 owns definitions, variants and canonical term IDs. The theorem should only store optional disambiguating link hints and erroneous-link exclusions. Don't copy the mathDef corpus into theorem data.

**Keep the schema lean:** Required fields can be populated mechanically in seconds from the same source and proof inspection. Do not add per-record complex audit forms to initial bulk ingestion.

## Catalog structure

- schema = maththm.theorems.v1
- contract_revision = 2
- total = actual length of records (if present)
- records = accepted searchable theorem objects, each with a unique stable lowercase ID.

### Required record fields

| Name | Value |
| --- | --- |
| id | Stable lowercase dotted/slug ID, independent of array position |
| entry_type | theorem, lemma, proposition, corollary or other_result |
| title | Optional descriptive or conventional name (may be null) |
| area | Mathematical subject/context |
| statement | Full unified displayed mathematical claim, with LaTeX as necessary |
| hypotheses, conclusions | Independently searchable lists of nonempty texts; preserve full logical scope in statement |
| hypothesis_tags, conclusion_tags | Separate arrays, may initially be empty |
| source_url | HTTPS page/document containing the theorem statement |
| statement_provenance | basis, transcription_status, source_text, locator, editorial_notes |
| proofs | One or more ACTUALLY INSPECTED proof references with url, locator, screening, accessed_on |
| acquisition | status = cursory_screened; batch_id; collected_on (YYYY-MM-DD) |
| mathematical_audit | status = not_audited initially |
| tag_provenance_defaults | hypotheses/conclusions origins: initial_editorial, source_literal or editor_approved |
| tag_annotations | List of later per-tag origin corrections; normally empty at intake |
| review_status | Temporary legacy site field: cursory_screened_unverified |

Optional: link_hints as phrase/mathDef-ID pairs, link_exclusions as a list of mathDef IDs, equivalence_sides for retrieval-only direction concepts, and proof_candidates for uninspected additional proof links.

### Source statement provenance

- basis: source_transcription, editorial_restatement_unverified, or editorial_restatement_reviewed.
- transcription_status: preserved, not_transcribed, or not_permitted.
- source_text: the ORIGINAL source wording if preserved, otherwise null. Do not label a paraphrase a transcription.
- locator: enough detail to find the result again (theorem number, page, section or anchor where available).
- editorial_notes: what changed, uncertainty, or a blank string if no edits.

The initial 20 prototype entries were editorial restatements, not verified copies, and now explicitly have source_text = null and status = not_transcribed. Their exact URLs remain intact for a later source-fidelity audit. The earlier statement_editorial field remains as historical metadata.

### Proof provenance

Each accepted proof reference requires HTTPS url, a retrievable locator, a screening status (cursory_screened, audited, or verified), and the date it was actually inspected. Mere reference to an inaccessible paper does not qualify as cursory-screened.

Optional proof_candidates store url and status = uninspected. They are not accepted evidence. A theorem with only proof candidates is not admitted to the public records array.

Mathematical-audit states anticipated later: not_audited, under_review, reviewed_with_findings, verified, rejected. The current prototype displays all theorems as unverified and therefore rejects setting verified in the accepted catalog until the site and audit procedures are upgraded together.

### Tags, links and equivalence

Search tags are editor interpretations, not mathematical implications. Initial per-side origins live in tag_provenance_defaults; later approved changes use tag_annotations objects containing side, tag and origin. The UI normalizes search terms without overwriting the human-readable tags.

Link hints preserve existing two-element arrays [visible phrase, mathDef V2 canonical or resolvable ID] and override automatic phrase disambiguation only within that theorem. Link exclusions suppress known bad targets in a particular theorem. The newer indexed phrase linker automatically recognizes a small curated set of common inflections and defers other ambiguity instead of guessing.

Equivalence sides may be indexed for both hypothesis and conclusion searches while displaying the theorem just once. This is retrieval, not proof or Boolean consequence generation.

## Minimal accepted-theorem intake recipe (not an engine)

1. Find a trustworthy statement location, and record a source-faithful unified claim and appropriate fidelity flags.
2. Extract hypotheses/conclusions, then initial lightweight tags.
3. Open a proof and check only whether it appears to present a finished proof; record direct reference, locator and inspection date.
4. Generate stable ID, batch identifier, and not_audited status.
5. Validate structure and publish. If a proof was not accessible or appears incomplete, keep the discovery out of the searchable records.

Do NOT spend this first pass verifying mathematical correctness, comparing all alternate proofs, searching dependencies, identifying subtle duplicate equivalences or performing elaborate editorial research.

Before implementing the harvesting engine, discuss a deliberately small minimum viable batch process, throughput, early-stop policy, and recovery/checkpoint budget with the user. The user wants several hundred genuine theorem records before revisiting major website interface decisions.

## Validation

- python -m scripts.theorem_schema data/theorems.json
- python -m unittest discover -s tests -v
- node --test tests/test_search.cjs tests/test_mathdef_v2.cjs tests/test_definition_links.cjs tests/test_ui_smoke.cjs

Structural validation does NOT certify mathematics.

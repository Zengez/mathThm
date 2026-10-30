# Phase 2 — durable GitHub Actions chapter preparation

The preparation pipeline produces **source-pinned, proof-free review inputs**
for the 9,675 active canonical Stacks candidates. It is **not** mathematical
reconstruction, validation, proof screening, or publication. Never treat
prepared material as Phase 3 eligible.

## Durable output

Pinned Stacks commit: `a04446e57ec1fbc252a871afcec7752fb2807b14` (spaces removed).

Output directories have this layout:

~~~text
harvest/phase2_prepared/a04446e57ec1/INDEX.json
harvest/phase2_prepared/a04446e57ec1/<chapter-stem>/MANIFEST.json
harvest/phase2_prepared/a04446e57ec1/<chapter-stem>/SECTIONS.jsonl
harvest/phase2_prepared/a04446e57ec1/<chapter-stem>/CANDIDATES.jsonl
~~~

Each chapter contains *all* indexed sections, even zero-candidate sections,
in physical order. Source excerpts exclude proof environments. Sections retain
chronologically ordered definitions and possible scope/event **leads**,
unresolved context issues, and references to prior editorial drafts. Candidate
packets include original source statements and preliminary Pass 2 fields, but
no new mathematical interpretations or eligibility decisions.

Each manifest includes the source and output SHA-256 digests. The index tracks
coverage; once all 115 chapters are prepared, 9,675 distinct candidate inputs
must be present.

**The chapter files are retained permanently in Git commits on the isolated
preparation branch.** Action artifacts are convenient additional ZIP snapshots,
but expire after 30 days; they are not the durable store.

## GitHub Actions

`.github/workflows/phase2-prepare-chapters.yml` supports manual
workflow dispatch once the workflow is registered on the default branch:

- **chapters** — `all` or comma-separated names such as `varieties.tex,flat.tex`
- **max_chapters** — maximum unprepared chapters in this invocation (0 = all)
- **persist** — commit/push each complete chapter immediately

For safety, commits are permitted *only* to
`feature/phase2-chapter-preparation` or `data/phase2-prepared`.
The workflow never writes to `main` or `codex/phase2-validation`.
A push changing the preparation workflow/scripts on the feature branch also runs incremental preparation of every missing chapter. Generated chapter commits do not retrigger it. The first completed test prepared Varieties; a subsequent full run successfully prepared all 115 chapters (9,675 candidate inputs).

It checks the pinned source, runs the regression suite, produces only missing
chapters, independently verifies hashes/coverage, commits each chapter, and
uploads a supplementary temporary Actions artifact.

A separate workflow, `.github/workflows/phase2-review-integrity.yml`,
provides read-only tests of the authoritative mathematical review registry and
population states. It does not approve statements.

Local invocation, with the pinned Stacks checkout at `upstream/stacks`:

~~~bash
python -m scripts.phase2_prepare_chapters --chapters all --only-missing --max-chapters 12
python -m scripts.phase2_verify_prepared --source-root upstream/stacks
~~~

For one chapter, supply `--chapters varieties.tex`. Use `--list-only` to
see what remains without modifying any files.

## Handoff to Codex

Do not merge the preparation branch into Codex's active validation branch
just to obtain input packets. Codex can fetch those files separately while
preserving its own working tree:

~~~bash
git fetch origin feature/phase2-chapter-preparation
mkdir -p .harvest_runs/prepared
git archive origin/feature/phase2-chapter-preparation harvest/phase2_prepared \
  | tar -x -C .harvest_runs/prepared
~~~

The packets will then be under
`.harvest_runs/prepared/harvest/phase2_prepared/a04446e57ec1/`.
If Git configuration prevents fetching, use a separate checkout of the prep
branch instead. Never modify review history just to access packets.

Before reviewing, Codex must reconcile candidate IDs with the *current*
authoritative approval ledger on its own branch. Prepared input snapshots
intentionally include already approved candidates. Codex must skip approvals,
not duplicate work.

Review complete sections in source order with shared proof-free evidence.
Preserve distinct mathematical reconstruction and independent source-first
validation. Record individual decisions and scoped holds in the existing
review manifest. Materialize only explicit approvals with content digests
using the established Phase 2 authoritative scripts.

## Important limitations

Preliminary hypothesis/conclusion fields and source-context event leads do
not establish logical equivalence. Codex must still independently judge
quantifiers, alternative hypotheses, equivalences, definitions, temporary
assumptions, existential witnesses, and mathematical notation. Proofs remain
excluded throughout Phase 2 preparation.

Offloading mechanical source work saves Codex from repeated indexing and
source navigation, but does not replace mathematical reasoning. Measure
actual credits before claiming a specific efficiency gain.

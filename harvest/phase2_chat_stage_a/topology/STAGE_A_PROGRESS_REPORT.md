# Topology chapter — Stage A completion report (2026-10-31) (2026-10-31)

Pinned Stacks revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`. Working branch: `work/phase2-stage-a-context-enrichment`.

## Source-first preparation and canonical scope

- Entire `topology.tex` covered: **30/30** complete physical sections (§§1–30, lines 17–6021), including 2 context-only introductory sections.
- Original source candidate environments: **161**. Canonical active candidates: **156**. Excluded noncanonical source environments: **5**.
- Prepared, source-scoped standalone statements awaiting independent Codex Stage B: **155**.
- Explicit Stage A `further_work_needed` holds: **1**.
- Already-authoritative-approved candidates regenerated: **0**. No Stage B approvals or Pass 3 promotions performed.
- Initial A0 work packets (§§3–12): 52 candidates; source-checked in the first two Stage A batches, not mechanically promoted on A0 flags alone.
- Fresh Stage A review (§§13–30): 104 active candidates, 103 ready and 1 held.

| Batch | Complete sections | Active | Ready | Further work |
| --- | --- | ---: | ---: | ---: |
| `batch_01_sections_01_07` | §§1–7 | 21 | 21 | 0 |
| `batch_02_sections_08_12` | §§8–12 | 31 | 31 | 0 |
| `batch_03_sections_13_20` | §§13–20 | 53 | 53 | 0 |
| `batch_04_sections_21_30` | §§21–30 | 51 | 50 | 1 |

## Exact unresolved hold

`candidate.stacks.97fdcbde7bf7e2308cf8b340` — `lemma-topology-quasi-separated-scheme`, §27 line 5469.
The source conclusion list ends with `\\item add more here.`, an unfinished mathematical result. The candidate is **not** ready for independent Stage B until the intended theorem wording is adjudicated. See `batch_04_sections_21_30/RECONSTRUCTIONS.jsonl` and `FURTHER_WORK_NEEDED.jsonl`.

## Source-specific clarifications

- Replaced the two late direct named-lemma references (§23 soberization, §24 spectral-limits open-basis family) using their pinned antecedents; all ready Stage A statements are free of direct `\\ref` links.
- Made explicit the otherwise unbound dimension function `\\delta:X\\to\\mathbf Z` at §20 and the indexing-category objects in §14.
- Scoped constructibility to a fixed topological space in §15 and the quasi-compact closed-subspace claim in §12/§15 terminology.
- Spelled out the Stone–Čech notation from the §25 section opening and preserved distinct definitions of universal closedness/Bourbaki-properness/quasi-properness in §17.
- Preserved item-wise premises and enumerated conclusions, especially the §15 generic-point conditional equivalence, §23 the paired lifting alternatives, §24 five-way spectral equivalence and dependent claims, and §28 stratification vocabulary.
- Named definitions remain terminology/context; no earlier theorem’s assumptions were imported. Ledger and after-section checkpoint records cover §§13–30 continuously and preserve their source introduction lines.

## Validation performed and limits

Construction-time JSON and JSONL serialization, 156 canonical IDs unique and aligned to pinned source label/section/line, 0 overlaps with the two historical approval files, 30 source section checkpoints, 155 ready + 1 held, 1 hold appended without loss to the global registry, no direct `\\ref` or `add more here` in ready statements, no original Stacks source or proof files modified.

**Not run:** repository-wide Python regression suite, independent Codex Stage B semantic/equivalence/proof validation. Stage A readiness is not theorem approval.

## Final scope-aware metadata audit

Eight additional local candidate partitions (topological characterizations, equivalences, and Stone–Čech existence/consequence) were reconciled to the full source statement. No change to 155 ready / 1 held.

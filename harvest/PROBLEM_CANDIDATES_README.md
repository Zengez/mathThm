# Deferred mathThm problem candidates — future discovery queue

**Status:** Set aside during the initial bulk discovery and prototype build. These are *not* rejected theorems or failed proofs. All canonical Pass 1 and Pass 2 decisions remain intact.

## One combined registry, three difficulty groups

- **[problem_candidates.jsonl](problem_candidates.jsonl)** — canonical unified registry: **1,304** records.
- **[PROBLEM_CANDIDATES_MANIFEST.json](PROBLEM_CANDIDATES_MANIFEST.json)** — current counts by difficulty, source batch, and structural subtype, plus the active-intake rule.

JSON Lines cannot contain prose section headings without breaking its data format. Instead, the records are ordered by `difficulty_group`, each record carries that field and a more granular `difficulty_subtype`, and the groups are described below. Each record also retains its stable candidate ID, original Stacks source statement and pinned URL, references, review notes, and available recovered source context.

### Group 1 — Inherited source context (`inherited_context`)

**862 records**. Statements refer to incomplete or unexpanded prior notation, standing assumptions, preceding definitions/constructions, or other source-dependent context. Their canonical status is `needs_context`. They require later source reconstruction rather than a guess at premises.

### Group 2 — Structurally difficult statements (`structural_complexity`)

**439 records**. Statements are available, but the hypotheses and conclusions cannot yet be separated with sufficient confidence. Their canonical status is `needs_structure`. Subtypes are *routing hints*, not formal verdicts:

| Structural difficulty subtype | Records |
| --- | ---: |
| Unconditional assertion or missing source boundary | 152 |
| Enumerated hypotheses, conclusions, or cases | 94 |
| Nested lists and case scopes | 54 |
| Equivalences or scope of an additional assertion | 48 |
| Editorially incomplete placeholders | 40 |
| Conditional scope | 33 |
| Diagrams or display-math scope | 18 |
| **Structural group total** | **439** |

Particularly, do not silently interpret joint premises as independent alternatives, upgrade a corollary to an equivalence, or fabricate a hypothesis for an unconditional theorem.

### Group 3 — Uncertain mathematical-result classification (`classification_uncertain`)

**3 records**, all in `trace.tex`, whose original Pass 2 status is `needs_classification`. They involve a conjecture known or asserted only in special cases, a conditional result assuming a conjecture, or an explicitly incomplete statement relying on unspecified unproven facts. These are **not** yet accepted mathematical results or rejected false positives.

| Original source label | Difficulty subtype |
| --- | --- |
| `theorem-conjecture-n-2` | `conjecture_special_case_claim` |
| `theorem-weil-II` | `conditional_result_assuming_conjecture` |
| `theorem-conjecture-l-bigger-2n` | `claim_dependent_on_unproven_assumptions` |

The three full statements are preserved in the same JSONL archive, along with their pinned source links and canonical IDs, and remain available for later review.

## Initial bulk discovery and prototype policy

1. Exclude **all three** difficulty groups in the registry from the active prototype/bulk candidate intake.
2. Only records currently marked `resolved` and classified `mathematical_result` in the canonical Pass 2 records may be *considered* for the later Pass 3 validation pipeline. A Pass 2 split is not independent mathematical or proof verification.
3. Do not delete, mislabel as a false positive, or auto-promote any deferred candidate.
4. Keep classification-uncertain records distinct from structural/context difficulties; their archival inclusion is not a classification decision.

## Rebuild for a later discovery phase

Canonical source: `harvest/batches/<batch>/pass1.jsonl` and `pass2.jsonl`. This combined registry is a reproducible snapshot, not a replacement for them.

The earlier generator was retired with the obsolete Pass 2 campaign. If a
later discovery phase requires a refresh, update the canonical derived registry
from the source Pass 1/2 data as a one-time operation—not by reviving the old
compatibility alias or adding a runtime lookup layer.

**Coverage invariant:** the registry must include exactly every candidate whose canonical Pass 2 status is not `resolved`, with zero unarchived unresolved IDs. Regenerate after future Pass 2 adjudications, and again before starting a later discovery phase. Resolved cases must be omitted from the single rebuilt registry. The source revision is pinned at `a04446e57ec1fbc252a871afcec7752fb2807b14`. No proofs were read or public theorem entries changed for this registry update.

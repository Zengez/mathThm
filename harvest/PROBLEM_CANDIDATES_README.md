# Deferred mathThm problem candidates — future discovery queue

**Status:** Set aside during the initial bulk discovery and prototype build. These are *not* rejected theorems or failed proofs. All canonical Pass 1 and Pass 2 decisions remain intact.

## One combined registry, two difficulty groups

- **[problem_candidates.jsonl](problem_candidates.jsonl)** — canonical unified registry: **1,301** records.
- **[problem_candidates_inherited_context.jsonl](problem_candidates_inherited_context.jsonl)** — legacy path retained as an *identical copy of the unified registry*, despite its historical filename. It now includes both groups.
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

## Separate classification queue

**Three** `needs_classification` candidates, all from `trace.tex`, remain separate pending an editorial/user decision. Their precise statements and provenance appear in [PASS2_RESUME_INVENTORY_2026-10-28.json](PASS2_RESUME_INVENTORY_2026-10-28.json) under `classification_details`. They are not among the 1,301 archived problems until a later explicit decision requires that.

## Initial bulk discovery and prototype policy

1. Exclude **both** difficulty groups in the registry from the active prototype/bulk candidate intake.
2. Only records currently marked `resolved` and classified `mathematical_result` in the canonical Pass 2 records may be *considered* for the later Pass 3 validation pipeline. A Pass 2 split is not independent mathematical or proof verification.
3. Do not delete, mislabel as a false positive, or auto-promote any deferred candidate.
4. Do not conflate the three separate classification cases with either deferred difficulty group.

## Rebuild for a later discovery phase

Canonical source: `harvest/batches/<batch>/pass1.jsonl` and `pass2.jsonl`. This combined registry is a reproducible snapshot, not a replacement for them.

```bash
python -m scripts.pass2_problem_candidates
```

Regenerate after future Pass 2 adjudications, and again before starting a later discovery phase. Resolved cases automatically disappear from both copies on rebuild. The source revision is pinned at `a04446e57ec1fbc252a871afcec7752fb2807b14`. No proofs were read or public theorem entries changed for this registry update.

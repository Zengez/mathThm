# Stacks standing-context atlas — first bounded review

**Pinned Stacks source:** a04446e57ec1fbc252a871afcec7752fb2807b14

**Completed:** 55 designated convention/notation/setup sections in 48 chapters read at source-excerpt level. Indexed all 115 main-book chapters for later lookup. No candidate statements or hypotheses changed.

This index is a **lead resource**, not a transitive theorem-context engine. Every record preserves a source locator, annotated likely scope, applicability caveats, and named source-context inheritance if explicitly written.

## High-value context families and warnings

- **Global:** ZF with choice, small-category default, commutative unital rings (zero ring allowed), unitary modules, positive integers beginning at 1.
- **Algebraic spaces:** Many chapters repeat big-fppf-site and fiber-product conventions; preserved as chapter-specific sources grouped under a shared family.
- **Stacks:** Properties of Stacks defines identification of spaces/schemes with associated stacks and 2-categorical conventions, then several later chapters explicitly inherit them.
- **Explicit scope changes:** Formal Spaces starts new standing conventions at its Conventions section (line 620); never retroactively apply them to earlier statements.
- **Named assumptions:** Chow Homology and Chow Groups of Spaces have distinct named setup situations with base/dimension-function assumptions that matter for standalone statements.
- **Caveats and counterexamples:** Etale Morphisms explicitly says Noetherian hypotheses will be repeated, so the chapter's frequent Noetherian setting is NOT itself a standing hypothesis; Moduli chapters override the default base to Spec(Z); one Intersection Theory source uses bold C for an algebraically closed field of arbitrary characteristic, not necessarily complex numbers.
- **Noncontext:** The Desirables chapter's Conventions section is an editorial wishlist, not a standing source convention.

## Files

- [Reviewed context atlas](stacks_standing_context_atlas_2026-10-28.jsonl): one annotated record per designated section.
- [Chapter lookup and explicit direct inheritance links](stacks_standing_context_lookup_2026-10-28.json): all 115 chapter entries, global context ids, repeated families and direct edges.
- [Original bounded source review excerpts](stacks_context_sections_2026-10-28_packets.jsonl): do not treat excerpt text as automatically applicable mathematical assumptions.
- [Manifest and scope counts](stacks_standing_context_manifest_2026-10-28.json).

## Candidate-review lookup rule

1. Look up the candidate's source chapter; inspect global and chapter-local entries, applying scope guards.
2. If a direct inherited convention is listed, open its target record. Do not recursively follow unrelated citations.
3. Retrieve the theorem's own section introduction and explicit local references **on demand**.
4. Translate only necessary and applicable source assumptions into fully standalone hypotheses; keep unrelated earlier results as proof dependencies, not hypotheses.
5. Only after standalone review should duplicate merges be confirmed and proofs screened.

**Not started:** exhaustive introduction/paragraph indexing, full standalone candidate expansion, Pass 3 proof checking. Source attribution: The Stacks Project Authors, The Stacks Project, GNU Free Documentation License; exact text is pinned to source links.

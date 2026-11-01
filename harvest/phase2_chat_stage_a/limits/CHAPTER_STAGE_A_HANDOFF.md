# `limits.tex` — source-ordered Stage A chapter handoff
Pinned revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`. Branch: `work/phase2-stage-a-context-enrichment`.
All **22** complete physical source sections accounted for; **111** source theorem-with-proof candidates, of which **100** are canonical active and **11** excluded. **94** prepared for independent Stage B, **6** marked `further_work_needed`, **zero** unprocessed active candidates.

Named setup ledger: `situation-descent` (§4), `situation-descent-property` (§8, explicitly reused in §18), `situation-limit-noetherian` (§22); the valuative criterion diagram from §15. Individual lemma hypotheses do not carry across environment boundaries. Original proof bodies and approved overlays were not changed.

## Batch breakdown
| Sections | Active candidates | Stage B-ready | Further work |
|---|---:|---:|---:|
| 1–8 | 49 | 49 | 0 |
| 9–16 | 32 | 32 | 0 |
| 17–22 | 19 | 13 | 6 |
| **1–22** | **100** | **94** | **6** |

## Specific unresolved source issues
- §19, `lemma-top-cohomology-functor` (line 4667): Conclusion (c) says formation of top direct images commutes with arbitrary further base change but explicitly refers to the proof for the comparison-map explanation. Specify the full quantifiers and canonical base-change isomorphism without reading a proof before a Stage B-ready split.
- §19, `lemma-higher-direct-images-zero-above-dimension-fibre` (line 4807): Part (2) imports both the assumptions and all conclusions of the preceding top-cohomology-functor lemma, including its proof-dependent part (c); the full conditions and canonical comparisons must be inlined safely.
- §19, `lemma-proper-top-cohomology-finite-type` (line 4888): The conclusion calls R^d f_* F an O_X-module, although a direct image under f:X->Y is naturally an O_Y-module. Resolve the pinned source mismatch without silently correcting the theorem.
- §19, `lemma-proper-top-cohomology-finite-presentation` (line 4964): The conclusion calls R^d f_* F an O_X-module of finite presentation rather than an O_Y-module. Resolve the pinned source mismatch without silent emendation.
- §22, `lemma-morphism-good-diagram` (line 5446): Requires careful reconstruction of two good diagrams and two scheme-theoretic-image inverse systems before the eventual morphism and uniqueness assertions can be made independently standalone.
- §22, `lemma-good-diagram-fibre-product` (line 5629): The four good diagrams, four inverse-system morphisms, their indices, and eventual cartesian/closed-immersion assertions are defined only through nested earlier lemmas. Their object and arrow identifications need verification before a safe standalone expansion.

## Validation boundary
Verified pinned locator/ID reproduction and uniqueness, complete-section traversal, explicit named-context and local diagram handling, active versus excluded candidates, and ready/hold reconciliation. Stage A is editorial; no proofs, independent Stage B mathematical validation, Phase 3 promotion, or repository Python regression suite were performed.

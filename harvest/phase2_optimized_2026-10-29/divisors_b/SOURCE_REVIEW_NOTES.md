# Independent source-first review context

Reviewer: authoritative_overlays. Pinned revision: a04446e57ec1fbc252a871afcec7752fb2807b14.

Read divisors.tex 3341–9492 in physical order before reading the new reconstruction records. Proof environments were removed before tool output. Read surrounding definitions and standalone theorem statements, including intervening sections. No proofs were screened.

Shared context used in the candidate comparisons:

- Complements of affine opens: dimension at generic points is at most one; equality has the separate density/closure guard. Noetherian versus locally Noetherian and separated versus affine-diagonal hypotheses vary between statements.
- Norms (3586–3605): a norm of degree d requires d >= 1, a multiplicative map of sheaves, its restriction to base functions g -> g^d, and the stated zero-locus property. Norm maps on invertible modules depend on this datum. These definitions are not global hypotheses on unrelated theorems.
- Relative effective Cartier divisors (3979–3985) require the divisor to be flat over the base, not the ambient scheme. The definition explicitly differs from some literature conventions.
- Conormal algebra (4295–4349): degree n is I^n/I^(n+1) on the closed-immersion neighbourhood. The canonical symmetric-algebra map is a quotient. The source's normal bundle terminology does not imply finite local freeness (4497–4500).
- Ringed-space regular sequences (4544–4580) use injectivity on successive quotient sheaves. Do not append the nonzero final quotient condition from the distinct ring-level convention. Regular ideal sheaves are tested locally on the support (4611–4642). The various regularity notions become equivalent only under the stated Noetherian hypotheses.
- Meromorphic functions (5855–5965): K_X is a sheafification of localizations at regular sections. General K_X,x need not be the total quotient ring; the later Noetherian/reduced hypotheses matter. Meromorphic pullback requires regular functions to pull back to regular functions. A regular meromorphic section means an injective multiplication map, not a holomorphic section.
- Weil divisors may be locally finite infinite sums on non-quasi-compact schemes (6585–6597). The order at a codimension-one point is a length-difference order, not a valuation unless a DVR assumption applies (algebra.tex 29802–29819). The Picard-to-class-group map is defined via nonzero meromorphic sections (6807–6825); no preceding normality assumption carries into unrelated lemmas.
- Relative Proj: distinguish finite type over A_0 from finite type over O_S. Twist sheaves need not be invertible in general grading. Logical alternatives in quasi-compactness are sufficient cases, not a conjunction or asserted conclusions.
- Blowups (8283–8319): Proj of the Rees algebra of the ideal; the exceptional divisor is its inverse image. Twists are invertible because this algebra is generated in degree one. Arbitrary blowups are not automatically finite type or quasi-compact. Strict transform uses the quotient by sections supported on the inverse image of the exceptional divisor (8780–8792), not an ordinary pullback.
- U-admissibility (9088–9107) requires existence of a finitely presented centre disjoint from U. The same morphism can have multiple centres. Shared centres in strict-transform comparison require the exact stated set-theoretic union condition.
- External exact definitions checked: ample family (morphisms.tex 2117–2132); rational maps on topologically dense opens (12585–12600); modification as proper birational map of integral schemes (13531–13536); Fitting ideals by minors (divisors.tex 1247–1280); defined pullback of an effective Cartier divisor (2580–2588); regular section (2777–2784).

Adversarial source concern to retain on hold: lemma-Pic-projective-space-UFD does not specify a positive projective dimension, although the asserted isomorphism with Z fails for P^0. Do not silently insert n >= 1 without recording a source-scope justification or source defect.

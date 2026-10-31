# A0 v2 examples: doing the easy work without doing the hard mathematics

**Date:** October 31, 2026  
**Pinned source:** The Stacks Project, `flat.tex` at `a04446e57ec1fbc252a871afcec7752fb2807b14`.

Use these as examples of **intermediate A0 work**, *not* completed standalone statements or source-equivalence certificates. A0 should leave A1 able to see exactly what has been copied, mapped and extracted, and exactly what difficult decision remains. Original source text and its pinned locator must always be preserved separately.

## Example 1 — Safe, straightforward prerequisite substitution

**Candidate:** `lemma-base-change-one-step`, `flat.tex:878`. Its opening says `Let S, X, F, s be as in Definition \ref{definition-one-step-devissage}`.

**Reference work A0 can complete:** Read `definition-one-step-devissage` at line 779. Its first four declarations give:

- `S` is a scheme.
- `X` is locally of finite type over `S`.
- `F` is a finite-type quasi-coherent `O_X`-module.
- `s` is a point of `S`.

**A0 proposed mechanical preface:** “Let \(S\) be a scheme, \(X\) a scheme locally of finite type over \(S\), \(\mathcal F\) a finite-type quasi-coherent \(\mathcal O_X\)-module, and \(s\in S\).”

Copy the remaining source statement and its one-step-devissage terminology *without* silently expanding every condition in that definition. Record a transformation replacing just the exact source phrase, with provenance `flat.tex:779`. **A1 remaining:** Verify the term-level dependence and full standalone semantics.

## Example 2 — Inherited lemma assumptions plus new assumptions

**Candidate:** `lemma-homothety-universally-injective`, `flat.tex:1820`. It explicitly imports assumptions and notation of `lemma-homothety-spectrum` (line 1782).

**A0 source-backed work to extract:**

- Base objects: ring map \(R\to S\) and \(S\)-module \(N\).
- Inherited conditions: \(R\) local with maximal ideal \(\mathfrak m\); \(\overline S=S/\mathfrak m S\) is Noetherian; \(\overline N=N/\mathfrak m_R N\) is finite over \(\overline S\).
- Definition of \(\Sigma\): elements of \(S\) that are nonzerodivisors on \(\overline N\).
- Candidate's *additional* conditions: \(S\) is local and \(R\to S\) local; \(S\) is essentially of finite presentation over \(R\); \(N\) is finitely presented over \(S\); \(N\) is flat over \(R\).
- Claimed result: each \(s\in\Sigma\) induces a universally injective \(R\)-module self-map of \(N\), and \(N\to\Sigma^{-1}N\) is \(R\)-universally injective.

**A0 output:** Store these source-derived lists and the exact source excerpt from the parent lemma. The inherited premise list can be inserted into a *provisional* preface because identity of \(R,S,N\) is explicit. **A1 remaining:** Verify subtle notation and the combined full claim; do not silently repair unusual source notation.

## Example 3 — Multi-hop setup and named Situation

**Candidate:** `lemma-compute-against-perfect`, `flat.tex:8078`.

The statement says “In Situation `situation-existence` let \(K\) be as in Lemma `lemma-compute-what-it-should-be`.”

**A0 must gather:**

1. The full `situation-existence` environment at line 8035: inverse system \((A_n)\) with surjective, locally nilpotent transitions; \(A=\lim A_n\); separated finite-presentation \(X/A\); \(X_n\) by base change; compatible finite-presentation modules \(\mathcal F_n\), flat over \(A_n\), with proper supports.
2. The full source statement of `lemma-compute-what-it-should-be` at line 8061, including the definition of \(K\) by derived limits.
3. The candidate's own perfect object \(E\), enumerated assertions and quantifiers.

**A0 output:** A context packet with two exact source locators and a provisional candidate preface. A1 should *not* have to find either source target again. **A1 remaining:** Verify the relationship between the data, \(K\), any specialized constructions, and the theorem's entire logical form.

## Example 4 — Difficult diagram, simple preliminary work

**Candidate:** `lemma-devissage-flat`, `flat.tex:687`, imports `lemma-elementary-devissage` at line 493.

The parent fixes a morphism \(f:X\to S\), a finite-type quasi-coherent \(\mathcal F\), a point \(x\), its image \(s\), and a constructed diagram with \(X', S', Z', Y', z',y'\), maps \(g,e,i,\pi,h\), and \(\mathcal G\). Retrieve the complete diagram and witness properties **verbatim** into a source packet.

The child has **two separate three-way equivalence groups**, one about flatness on neighbourhoods and one about flatness of stalks. **These are both conclusions, not inherited assumptions.**

**A0 output:** source parent excerpt + symbols/objects inventory + two indexed conclusion groups + source locations. **A1 remaining:** Precise scope and diagram/witness substitution. A0 is successful even if it cannot safely write the final combined theorem.

## Example 5 — Explicit hypotheses/conclusions with no inherited reference

**Candidate:** `proposition-finite-type-flat-at-point`, `flat.tex:2476`.

The original statement expressly gives \(f:X\to S\), \(\mathcal F\), \(x\), \(s=f(x)\), followed by an “Assume that” list:

1. \(f\) is locally of finite presentation;
2. \(\mathcal F\) is of finite type;
3. \(\mathcal F\) is flat over \(S\) at \(x\).

The result asserts existence of an elementary étale neighbourhood and an open scheme \(V\) with the specified pullback properties. A0 should transcribe the three premises and the **full original conclusion** as separate source-literal fields, without condensing any of its quantifiers.

**A1 remaining:** Check whether terms and conclusions are standalone, not spend time rediscovering the three explicitly stated premises.

## Example 6 — Avoid a bad mechanical split

**Candidate:** `lemma-h-induced`, `flat.tex:10482`.

This statement has a `\begin{enumerate}` with multiple internal “If ... then ...” clauses. The first `Then` in the source is *not* an overall separator between theorem hypotheses and theorem conclusions.

**A0 output:** list the main given objects and **each numbered conditional clause as its own source-literal unit**; preserve the outer list and all quantifier scopes. A1 handles semantic reconstruction of the grouped claim.

A0 should **never** automatically treat material before the first `Then` as the complete hypotheses. The first Medium run's "before/after" partition was only a locator.

## Example 7 — Long dependency chain, still worthwhile mechanical work

**Candidate:** `lemma-proper-support`, `flat.tex:8244`.

Explicitly references `situation-existence` (8035), `lemma-compute-what-it-should-be` (8061), and `lemma-finitely-presented` (8180). A0 can extract all three full source statements (and a one-level nested dependency map) and list the symbols \(A_n,A,X,X_n,\mathcal F_n,K,W\) with their source origins.

**A1 remaining:** Verify the role of \(W\), any shrinking and the precise conclusion. Do not stop at "context needed" before extracting the three source targets.

---

## A0 completion checklist for a single candidate

A candidate is *prepped at A0* when the overlay shows its source statement; scope/ledger snapshot; all direct reference locations and relevant setup excerpts; explicit local declarations/conditions and list/implication structure; proposed safe copied fragments (if any); and concrete remaining tasks. A0 completion says nothing about whether its theorem is standalone or mathematically source-equivalent.

For sections with many shared references (e.g., the five+ candidates importing `situation-existence`), **resolve the Situation once per section or batch**, attach its stable context ID to each candidate, and avoid re-reading the same source for every candidate.

Do not use these examples to overwrite historical A0 v1 records or any Stage A / Codex approvals.
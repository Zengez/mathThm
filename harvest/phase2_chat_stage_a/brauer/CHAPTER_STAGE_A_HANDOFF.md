# Stage A handoff: Brauer groups

Pinned source: `a04446e57ec1fbc252a871afcec7752fb2807b14` (`brauer.tex`), §§1–8. Active identities: 25, ready for independent Stage B: 23, precise further-work holds: 2; 2 inactive source environments excluded.

The k-field and unital right-module conventions (§2), finite/simple/central algebra definitions, similarity definition (§5), and splitting-field definition (§8) were checked in source order. Original claims and enumeration retained; missing field convention and two explicit term definitions materialized without converting definitions into hypotheses.

## Held cases
- `lemma-rieffel` L91: The source says A coincides with the bicommutant of its right ideal M; clarify the precise canonical action A→End_{End_A(M)}(M), sidedness and whether 'coincides' is equality or canonical isomorphism (brauer.tex L91-117).
- `lemma-automorphism-inner` L510: The unqualified 'automorphism of A' must be interpreted as a k-algebra automorphism; arbitrary ring automorphisms may act nontrivially on the center k and need not be inner. Confirm the intended quantifier against brauer.tex L33-37 and Skolem-Noether L483-509 before promotion.

All 8 source sections are checkpointed. Candidate IDs match active registry. No original candidate or proof text changed; no independent equivalence validation or proof screening was performed.

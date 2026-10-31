# Third Stage A0 calibration: topology.tex §§3–12 — 2026-10-31

**Working branch:** `work/phase2-stage-a-context-enrichment`. **Pinned Stacks revision:** `a04446e57ec1fbc252a871afcec7752fb2807b14`.

**Scope:** Read complete source §§1–2 (context only), then source §§3–12 in order (lines 17–1999). Two five-candidate-bearing-section batches:
- `batch_01_sections_03_07` — 21 eligible active candidates, 1 noncanonical source statement excluded, 7 complete physical sections accounted for
- `batch_02_sections_08_12` — 31 eligible active candidates, 1 noncanonical source statement excluded, 5 complete physical sections accounted for

## Eligibility gate — verified BEFORE writing packets

The source contains **54 theorem-like labelled environments**, **52 active canonical candidates**, and **2 excluded noncanonical environments**:
- `lemma-connected-fibres-quotient-topology-connected-components` at line 720 (`candidate.stacks.eec369ce80c5f2b94250e114`)
- `lemma-connected-component-intersection` at line 1815 (`candidate.stacks.e835d27f94934c4429f812bb`).

The `active_candidate_ids.jsonl` registry was loaded through its pinned Git blob (**9,675 IDs**), along with both files named in `PHASE2_AUTHORITATIVE_REGISTRY.json` (**655 authoritative approvals**). No selected ID was already in the 655 approvals. Historical independent validation files in the branch were checked for overlap, with **zero matching independently reviewed identities**. At selection there were no `topology` A1 or A0 manifests. These are therefore **eligible source IDs at the time of selection**, though any later concurrent changes must be checked again before A1 consumes the packets.

## Output and extraction metrics

| Metric | Result |
|---|---:|
| Complete candidate-bearing sections | 10 |
| Complete physical sections checkpointed | 12 |
| Eligible candidate work packets | **52** |
| Distinct packet candidate IDs | **52** |
| Literal working hypothesis/setup extraction | **49** |
| Literal working conclusion/claim extraction | **52** |
| Short unconditional assertions with no separate hypothesis field | **3** |
| Enumerated source groups | **22** |
| Numbered items preserved | **61** |
| Item-specific assertion/guard packets | **55** |
| Other `If`, `Moreover` or `In particular` clause leads | **22** |
| Explicit `\\ref` occurrences in the candidate statements | **0** |
| References resolved / unresolved | **0 / 0** |
| Named source definition events | **15** |
| Total scoped ledger entries | **17** |
| Source-backed inheritance preface suggestions | **0** |
| Candidates still requiring A1 mathematical checks | **52** |
| Stage A/Stage B/Pass 3 readiness changes | **0** |
| Proofs mathematically reviewed | **0** |

The **zero direct statement references is a property of these source statements**, not evidence of incomplete reference-search tooling. Relevant preceding definitions were indexed as terminology context; no definition was automatically added as a theorem premise. There were no source-explicit named inherited setups that justified a confident preface insertion; the absence of safe substitutions is not an error.

### Work that A1 can reuse

- Every eligible packet retains the verbatim original statement, source label and line, canonical ID, pinned source URL, source-order section, scoped context/definition leads, and a recorded list of easy tasks done and remaining tasks.
- Familiar implications such as `lemma-graph-closed`, `lemma-section-closed` and `lemma-subbase-theorem` have their visible antecedent and conclusion preserved separately, **without mathematical approval**.
- Equivalence lists such as `lemma-Hausdorff` and `lemma-catenary` retain each numbered condition as a logical assertion rather than turning them into premises.
- `lemma-locally-connected` and `lemma-open-morphism-quotient-topology` have enumerated results and subsequent textual consequences preserved.
- `lemma-closed-union-connected-components` has its three enumerated hypotheses distinct from the separate equivalent-conditions list.
- Per-item conditional statements (for example `lemma-sober-local`) retain individual guards instead of a false global hypothesis.

### Limitations and integrity

The working hypothesis and conclusion fields are **source-literal scaffolding**, not standalone or semantically certified splits. For more complicated statements, A1 still needs to verify quantifier scope, implicit topological conventions, source-defined terminology, guarded lists, multi-claim logical form and mathematical equivalence. The three unconditional assertions rightly remain without a fabricated separate premise field.

All ten artifact files (five per batch) were created under `harvest/phase2_chat_stage_a0/topology/`. JSON/JSONL parsing, manifest counts, 52 unique IDs, ten eligible candidate-bearing section counts, two exclusions, ledger row counts, and twelve post-section checkpoints were verified. **No automated project regression suite or independent mathematical validation was run.**

This calibration is substantively different from the earlier unsuccessful `varieties` demonstration: eligibility was checked against the full active and approval registries before producing any candidate packet. The results show improved routine source-structuring output, but **do not establish how much elapsed time or High-thinking effort A1 will save** without a later independent A1 audit.

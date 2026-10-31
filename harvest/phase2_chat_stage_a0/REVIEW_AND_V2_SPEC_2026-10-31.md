# Audit and A0 v2 correction — 2026-10-31

**Scope:** `flat.tex` §§1–42, pinned Stacks Project source `a04446e57ec1fbc252a871afcec7752fb2807b14`. The original A0 pass was run at **Medium thinking**, as confirmed by the user. This audit is a *subsequent* higher-effort review of its work products, not a second Medium benchmark. The purpose is **routine work removed from A1**, not how many final standalone theorems A0 certifies.

## What was wrong with the initial A0 output

The original A0 calibration produced 231 candidate overlays, 42 section checkpoints, 10 obvious inherited-context holds, and **zero** rewritten statements. The generic `a0_no_changes_needed` status appeared 221 times, but that did *not* mean there were no straightforward tasks for the candidate.

Inspection of the source statements finds **at least 40 explicit inherited-context forms** of the most obvious kinds; **33** had been marked `a0_no_changes_needed`. Specifically:

- `In Situation \\ref{...}`: **28 instances, 27 not flagged** as inherited context.
- `Let ... be as in Definition \\ref{...}`: **6 instances, all 6 not flagged**.
- Other obvious `Assumption(s) and notation as in ...` patterns were generally recognized by the first pass, but references still were not expanded.

These categories are source-phrase detections, **not** mathematical findings that all 40 require added assumptions. They prove the original pattern-based triage was too narrow. In particular, **nine named `situation` environments** occurred in the 42-section window; the first ledger indexed definitions but omitted them. Some of these setups are substantive (for example the inverse-system setup in `situation-existence` at `flat.tex` line 8035 and its derived counterpart at line 8378).

The first A0 records also failed to offer source-grounded prerequisite text, a statement premise/result skeleton, or a per-candidate list of easy tasks already completed. A generic hold left too much lookup/retyping work for A1.

## Improvements actually implemented in repository artifacts

The **original A0 results are preserved unchanged**. Four new `A0_WORKPACKETS_V2.jsonl` sidecars—one per original `flat` batch—now supply **231 structured, source-based work packets**, one per candidate. Each includes:

- Original pinned candidate text/ID/source locator, preserved unchanged.
- **Literal structure cues:** `Let`, `Assume`, `If`, `Then`, `In Situation`, equivalence markers, enumeration presence, and (when present) the text before/after the first `Then` **as an unverified source partition**. No naive before/after split is called a final hypotheses/conclusions list.
- **Every literal statement-time `\\ref` reference:** its contextual role (named Situation, explicit inherited setup, possible example/definition/equation, or other reference lead), original surrounding text, and any exact same-file target's full theorem/definition/Situation body (up to a bounded stored length), type, line and pinned URL. The target is **evidence**, not an assertion that it should be imported as a premise.
- Named **`easy_tasks_completed`** with evidence and **`a1_remaining_tasks`** specifying which references still require scope/object correspondence review.
- An explicit `candidate_math_ready:false` and no Stage A, Codex, proof or publication promotion.

**Source coverage of the v2 sidecars:** 231 candidate packets, **87** candidates containing at least one source reference, of which **58** contain references classified as possible setup/context leads and **29** other referenced-source leads. **144** have no explicit `\\ref` in the statement. Across these references, **31** remain without a target found in this pinned `flat.tex` source (many are expected to be cross-chapter and still need exact source lookup). These are *reference retrieval counts*, not accuracy or standalone readiness counts.

The separate `flat/CONTEXT_EVENTS_V2.jsonl` records **27 source environments** (nine Situations and 18 Definitions) through section 42, with labels, source excerpts, source line and non-auto-inheritance guards. This corrects the material omission of named Situations in the first pass.

All 231 candidates remain unverified, and the original `A0_RECONSTRUCTIONS.jsonl`, original ledger/checkpoints, A1 and Stage B records are untouched. New packets are auditable research aids, **not** proof that a complete scoped ledger has been semantically adjudicated.

## Examples of how this removes work

1. **`lemma-homothety-universally-injective`, line 1820:** the first pass said "needs inherited context." The v2 packet now retrieves the exact earlier `lemma-homothety-spectrum` at line 1782, including the local-ring hypotheses, \(\overline S\), \(\overline N\), and multiplicative subset \(\Sigma\). A1's remaining question is how to combine those literal premises with the new four conditions, not how to locate them.
2. **`lemma-base-change-one-step`, line 878:** the first pass said "no changes needed" despite `Let S,X,F,s be as in Definition ...`. The v2 packet retrieves `definition-one-step-devissage` (line 779), with four opening object assumptions and the definition's diagram and conditions. Medium can safely copy the four initial object declarations into a proposed preface without resolving the full term definition.
3. **`lemma-compute-against-perfect`, line 8078:** the first pass missed both the named Situation and the inherited \(K\). The packet now locates `situation-existence` (line 8035) and `lemma-compute-what-it-should-be` (line 8061), preserving their setup text. A1 must still check contextual alignment and the exact mathematical formulation.
4. **`proposition-finite-type-flat-at-point`, line 2476:** no cross-reference is needed. The packet identifies literal `Let`, `Assume that`, `Then`, and an enumerated assumption block, so A1 can organize the three plainly stated assumptions without re-reading for structural landmarks.
5. **`lemma-devissage-flat`, line 687:** two equivalent-conditions lists must remain **two logical equivalence assertions**, not additional theorem hypotheses. The packet retrieves `lemma-elementary-devissage` (line 493) and records the two enumerations as structural cues; A1 handles the difficult diagram/witness match.

See [A0 v2 training examples](A0_V2_TRAINING_EXAMPLES.md) for explicit sample completions and the expected A1 boundary.

## New operational rule

Read [STAGE_A0_PREPASS.md](../../STAGE_A0_PREPASS.md) (at repo root) for the updated mandatory **work-removal** procedure. Every candidate should emerge with a source/verbatim statement, a scoped ledger snapshot, a full reference packet, a low-inference premise/result skeleton where safe, a list of completed mechanical tasks, and precise work remaining. **Do not stop at "this needs higher thinking."** Do all the easy independent pieces first.

### Calibration and selection clarification

The approximately **200-section jump was just an overlap-avoidance buffer** while a separate A1 chat was progressing. There is no mathematical or operational need to reproduce that precise distance; select a genuinely nonoverlapping source-order window based on current manifests. This audit does **not** establish an exact +200 offset, and it does not need to.

The initial run really used Medium, per the user's confirmation. No reliable *time/cost saved in A1* measurement exists yet; neither the new v2 packets nor the user's model-setting confirmation establish a speedup. The next useful test is to ask Medium to **produce these v2 packets directly** for a fresh small section window, then have A1 judge how much necessary manual reconstruction remains.

## Validation and unresolved cautions

- Candidate IDs in all four sidecar batches map one-to-one to the original 231 source fingerprints; **canonical active-pool and newer Codex approval registry reconciliation remains pending** because the connector could not retrieve every large registry artifact in the earlier run. No current approvals or canonical data were changed.
- The retrieved source target may itself invoke nested context, and a source `situation` environment is not automatically an ambient assumption outside its explicit use.
- Some `\\ref` labels are cross-chapter or equation/list labels; do not turn them into hypotheses.
- Literal `Then` cues do not accurately split nested conditionals or enumerated equivalence statements without additional scoping checks.
- No full source-equivalence or regression suite was run; no claims of mathematical validation, standalone readiness, Codex completion, Pass 3 eligibility, or publication.

**Next checkpoint suggestion:** Audit a dozen A0 v2 packets with High thinking, refine any missing nested-context lookup, then run a *new* Medium batch with the improved rubric and compare task completion, error rate and A1 effort against this baseline.

## Final work-packet integrity and literal extraction checks

After the initial audit, the four v2 work packets were further enhanced with **source-literal** enumerated list items and local declaration/premise cues. The final re-read verified:

| Item | Count |
| --- | ---: |
| V2 work packets, one-to-one with original A0 candidates | **231 / 231** |
| Distinct candidate IDs | **231** |
| Enumerated source groups extracted | **96** |
| Source-literal enumeration items extracted | **288** |
| `Let` / `Set` / `Denote` / `Assume` / `Suppose` source fragments extracted | **435** |
| Named source Situations indexed | **9** |
| Named source Definitions indexed | **18** |
| Unauthorized Stage A/Codex readiness fields in v2 packets | **0** |

All four v2 files parsed successfully, and every packet's source text and candidate ID matched its original v1 overlay exactly. These are **structural/extraction checks**, not mathematical correctness claims; regex-derived enumerations and source fragments can still require nested-scope correction by A1. The unrun full regression suite and outstanding canonical/approval-registry crosschecks must not be implied by these results.

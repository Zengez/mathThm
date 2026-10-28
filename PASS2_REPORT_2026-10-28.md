# Pass 2 intake report — October 28, 2026

**Scope:** Both completed Stacks Project Pass 1 batches. The raw candidates were extracted from pinned Stacks LaTeX result environments with nearby apparent proof markers. The second run finished with 2,022 candidates, making **3,122 unique source-pinned candidate IDs** across the two source batches. Wikipedia has not yet contributed candidates.

## Results after conservative syntax triage and 20 light statement-only editorial spot checks

| State | First batch | Second batch | Total |
| --- | ---: | ---: | ---: |
| Pass 1 raw candidates | 1,100 | 2,022 | **3,122** |
| Pass 2 classifications recorded | 1,100 | 2,022 | **3,122** |
| Apparent mathematical results (based on Stacks result environment and source statement) | 1,100 | 2,022 | **3,122** |
| Hypotheses/result text split recorded | 587 | 987 | **1,574** |
| Needs source context / inherited notation | 105 | 212 | **317** |
| Needs clause-structure analysis (lists, diagrams, no safe boundary, etc.) | 408 | 823 | **1,231** |
| Needs more Pass 2 work | 513 | 1,035 | **1,548** |
| Pass 3 proofs screened | 0 | 0 | **0** |
| New public catalog entries | 0 | 0 | **0** |

**Interpretation is essential:** The result classification is **provisional and source-driven**, not mathematical verification. A Stacks lemma/proposition/theorem/corollary environment accompanied by an adjacent apparent proof marker is strong superficial evidence that the text is intended as a mathematical result, not an exercise or speculation. No candidate was positively identified as a non-result in this shallow screen. That does NOT mean an independent reviewer established the validity or self-contained completeness of all 3,122. No proofs were read.

The majority of the 1,574 resolved splits are **mechanical/syntax-only**; 19 short mathematical statements were separately given light editorial hypothesis/conclusion splits and one context-dependent construction was explicitly retained for context review. The mechanically resolved splits are **not certified semantic decompositions**, and must remain distinguishable from editorially reviewed ones. Their source statements are preserved without restating mathematical claims by speculative paraphrase.

## Workflow and evidence

- [Conservative automated Pass 2 run](https://github.com/Zengez/mathThm/actions/runs/40724519845): successfully classified/triaged both source batches. Corrected an issue caught by a spot check: statements beginning “In Situation …” must not silently be considered self-contained.
- [Light editorial spot-check run](https://github.com/Zengez/mathThm/actions/runs/40724807213): succeeded with 20 statement-only reviews. This added 19 explicit short-result splits (14 first batch, 5 second batch) and kept one “This construction …” claim in the context-dependent queue.
- `scripts/pass2_fast_stacks.py`: deterministic, bounded source-statement-only classification/splitter. It never reads the proof or performs mathematical background research.
- `harvest/batches/<batch>/pass2.jsonl`: one Pass 2 decision per raw candidate, keeping both `result_classification` and `context_status` with `review_method` and `split_confidence`.
- `harvest/batches/<batch>/needs_more_investigation.jsonl`: all currently unresolved Pass 2 statements, with source and proof URLs. These entries have **not failed proof screening**; they are pending statement extraction.
- `harvest/batches/<batch>/pass2_summary.json` is the **initial mechanical pass** (before 20 editorial fixes); `pass2_editorial_summary.json` holds the **current counts** after spot checks.
- `harvest/pass2_editorial_spotchecks.json` records the 20 explicit statement-level choices with lightweight explanations.
- `checkpoint.json` records final numbers and the absence of Pass 3 processing.

## Examples and quality findings

**Straightforward conditional:** “Let $R \to S$ be a ring map ... If $M$ is finite as an $R$-module, then $M$ is finite as an $S$-module.” The assumptions and conclusion can be split across the explicit *then* without changing their wording.

**Inherited setup:** “In Situation \ref{situation-descent} if $S$ is affine, then ...” is not self-contained; Pass 2 now sets `needs_context`, despite the clear grammatical *then*.

**Short unconditional result:** “A composition of monomorphisms is a monomorphism.” This was classified as a mathematical result, but ordinary syntax doesn't provide a literal assumption/conclusion boundary. Its editorial split uses a condition on two composable monomorphisms and a conclusion about their composite.

**Local construction:** “This construction gives the cup product.” Its assertion appears in a mathematical result environment, but the referenced construction is not contained in the text. The decision remains `needs_context`.

**Complex results:** Statements with enumerated equivalences, commutative diagrams, or long chains of hypotheses remain `needs_structure` unless a faithful split was evident. Avoid guessing quantifier scope.

## Next action and limits

Continue **Pass 2 statement review** for 1,548 unresolved candidates, prioritizing context-dependent statements and then structural multi-clause results. The `pass2-packets` command is explicitly designed to continue presenting unresolved entries **even if a preliminary Pass 2 triage record already exists**; don't skip them as done merely because the `pass2.jsonl` file contains an entry. Edit an existing decision using `pass2-apply --replace` only after an intentional improvement. Checkpoint counters can be rebuilt with `status`.

No proof inspections, math-theorem correctness audits, Pass 3 decisions, mathematics research cascades or site publication took place in this run. The existing public theorem catalog remains unchanged.

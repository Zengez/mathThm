# Wikipedia Stage A reconciliation and match against existing mathThm (November 4, 2026)

**Completed.** All four Wikipedia editorial workers have been reconciled by stable candidate ID, with no duplicate, foreign, or missing IDs. The 984 prepared statements have been compared against all 3,963 already-published mathThm theorem entries, without mathematical proof audits or re-review of prior Stacks decisions.

## Counts

| Outcome | Count |
| --- | ---: |
| Previously unmatched Wikipedia URLs | 1,121 |
| Editorially prepared standalone statements | **984** |
| Held for incomplete/ambiguous source text, with reasons retained | **137** |
| Existing published mathThm statements compared | **3,963** |
| Additional *unambiguously identical* statements located | **0** |
| Newly attached external Wikipedia proof links | **0** |
| Prepared statements retained for subsequent Wikipedia intake | **984** |
| Algorithm's higher-scoring pairs checked and identified as nonmatches | **11** |
| Earlier Wikipedia proof links preserved | **13** |

The 11 shortlisted comparison pairs turned out to be **different mathematical theorems** despite overlapping terminology or notation (e.g. Euler's criterion vs Fermat's little theorem; quotient rule vs mean value theorem; Darboux's theorem vs Rolle's theorem). These were deliberately *not* merged; see `shortlist_nonmatches.jsonl`.

## Procedure

The existing theorem catalog contains 3,963 theorems, largely approved Stacks results plus the 20 initial prototypes. Wikipedia Stage A has already removed the 13 obvious matches from the first title-only pass.

This further pass compared full statements and independent hypothesis and conclusion text using a sparse lexical similarity index. Only uniquely matched *identical* structured claims (or near-identical text simultaneously in all three fields) could have been accepted automatically. The high-score diagnostic list was checked once for obvious false positives. The comparison **did not** do deep equivalence proofs, search additional research sources, or try to eliminate all potential duplicates. Some duplicates may remain by design.

The previous Wikipedia proof overlay `data/wikipedia_proof_links.json` is preserved; because no new safely identical candidate was found, no extra proof link was added. No new Wikipedia theorem is published in this stage.

## Permanent deliverables

- `work/wikipedia-stage-a/20261103/reconciled/decisions.jsonl`: all **1,121** Wikipedia decisions with original text, worker attribution, and stable IDs
- `work/wikipedia-stage-a/20261103/reconciled/prepared_statements.jsonl`: the **984** structured, editorially prepared statements
- `work/wikipedia-stage-a/20261103/reconciled/held_statements.jsonl`: all **137** held records with their reasons and provenance
- `work/wikipedia-existing-match/20261104/unmatched_prepared.jsonl`: the **984** retained candidates after comparison
- `work/wikipedia-existing-match/20261104/unmatched_prepared_urls.txt`: exact, complete URL queue for the next stage
- `work/wikipedia-existing-match/20261104/shortlist_nonmatches.jsonl`: the **11** non-equivalent pairs briefly adjudicated
- `work/wikipedia-existing-match/20261104/REPORT.json`: automatic comparison counts
- `scripts/reconcile_wikipedia_stage_a.py` and `scripts/match_wikipedia_prepared_to_existing.py`: deterministic, rerunnable reconciliation and conservative match tooling

**Next content step:** Apply the existing cursory proof-accessibility/completeness gate to the 984 prepared *new* Wikipedia statements, linking directly to source proof headings. Only proof-screened candidates should be admitted to the publication pipeline; proof correctness remains a separate audit. Keep all 137 held candidates until the missing source conditions can be recovered. Do **not** reopen the approved Stacks theorem corpus or redo the duplicate research.

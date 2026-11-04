# Wikipedia proof-content screening: one-time retry of 224 inconclusive pages

**Completed November 4, 2026.** The original structural screening found 706 proof-looking sections, 54 nonpasses, and 224 inconclusive Wikipedia pages. Most failures were HTTP 429 (Too Many Requests), not indications that the article lacked a proof.

We re-requested **only those 224 inconclusive URLs**, once, with a single sequential runner and 1.5-second delay between candidates. A safeguard would have stopped at four consecutive HTTP 429 failures; it was **not triggered**. No recurring schedule was set.

## Final result

| Outcome | Initial run | After targeted retry |
| --- | ---: | ---: |
| Prepared Wikipedia theorem candidates | 984 | 984 |
| Proof section visibly contains argument-like content | 706 | **920** |
| No substantive proof section found | 54 | **64** |
| Inconclusive / inaccessible / deferred | 224 | **0** |
| Earlier held statement candidates (not screened) | 137 | **137** |

Of the 224 retried pages, 214 passed the same structural rule and 10 returned a concrete nonpass: 9 proof sections too thin/uninformative and 1 article without a proof-labeled section.

Proof validity, correctness, completeness, and theorem identity were **not** checked. No theorem has been admitted to the public catalog by this workflow.

## Permanent evidence

- `REPORT.json`: final counts and reasons.
- `retry_decisions.jsonl`: exactly 224 per-URL outcomes; retains initial failure reason, new section URL and screening evidence.
- `newly_screened_candidates.jsonl`: 214 additional prepared candidates with verified proof-section anchors and cursory presence metadata.
- `newly_no_visible_proof.jsonl`: 10 additional held candidates.
- `still_inconclusive_or_deferred.jsonl`: empty, confirming there were no remaining access failures.
- `newly_screened_urls.txt`: direct page URLs of the additional 214 passes.

The original **706 accepted** candidates remain in `work/wikipedia-proof-screen/20261104/proof_screened_candidates.jsonl`. Together with this retry's **214 new passes**, these comprise the **920 proof-presence-screened Wikipedia candidates** ready for the established subsequent intake/publication process. The original 54 nonpasses, new 10 nonpasses, and 137 Stage A source-clarity holds remain separate.

The original scan and URL classification are completed, and **no periodic Wikipedia dump or retry workflow has been installed**.

# Final Wikipedia theorem URL classification (verified 2026-11-03)

Source branch: `data/wikipedia-theorem-classification` at `864a3b08ffbdf3b87dce007b4f76993e435f3a4b`.

The original harvest, automated classification, and reviewed source records under `harvest/wikipedia_classification/20261001/` remain unchanged. This is **binary page-subject identification only**, not a mathematical proof/content review.

## Final counts

| Category | Count |
| --- | ---: |
| Original URLs, unique | 2,066 |
| Previously accepted automatically | 840 |
| Previously rejected automatically | 73 |
| Chat-reviewed queue | 1,153 |
| Newly accepted from review (after verification) | 294 |
| Newly rejected from review (after verification) | 859 |
| **Final accepted** | **1,134** |
| **Final rejected** | **932** |
| Remaining unclassified | 0 |
| Duplicates or overlap | 0 |

## Review and verification provenance

The first full semantic review accepted 257 and rejected 896 of the 1,153 queued URLs. A second pass **reviewed all 969 rejected URL titles and metadata** (including the 73 originally rejected), focusing on false negatives such as former conjectures, named mathematical bounds, solved impossibility problems, identities, decompositions, and other result pages. Wikipedia pages and external references were consulted selectively when metadata was insufficient.

That verification reclassified **37** of the 896 rejected reviewed entries as accepted, with individual concise reasons in `verification_corrections_20261103.jsonl`. The six `decisions_0*.jsonl` files were updated with the final classifications and record the previous decision for every changed entry. Original automatic decision files remain intact. Rota's excluded-minors conjecture is a borderline inclusion because a proof was announced but not published; this is recorded explicitly and is not a proof-quality judgment.

## Final outputs

- `accepted_urls.txt`: all 1,134 accepted URLs.
- `rejected_urls.txt`: all 932 rejected URLs.
- `decisions_01.jsonl` through `decisions_06.jsonl`: final decisions for all 1,153 reviewed URLs, preserving provenance.
- `verification_corrections_20261103.jsonl`: all 37 changes, reason and prior classification.

The 2,066 original URL IDs were compared with the two final lists: **exact set equality**. There are no duplicate URLs, accepted/rejected overlap, missing URLs, or unresolved reviewed entries.

# Wikipedia accepted URL → already-published theorem proof-link pass

Date: 2026-11-03. Source: **1,134 accepted URLs** from `work/wikipedia-final-binary-review-20261103` (classified against Wikipedia 2026-10-01 harvest). The theorem baseline is the public **3,963-record** catalog from `main`.

## Completed results

- **13 Wikipedia URLs** linked to **12 existing theorem IDs**.
- **1,121 URLs** retained intact in `unmatched_urls.txt` for new-content discovery.
- Every accepted URL appears in exactly one of `matches.jsonl` or `unmatched_urls.txt`; `decisions.jsonl` records all 1,134.
- No mathematical theorem or proof validation, theorem extraction, record merging, or new theorem publication was performed.

## Scope and matching policy

This is **deliberately a high-precision, low-recall pass**. A match requires a unique normalized theorem-title equivalence in the current catalog, and a Wikipedia proof-section heading with a direct fragment URL. Ambiguous matches, paraphrases, similar statements with different titles, and URLs without a confirmed proof fragment remain unmatched. It is expected that many genuine duplicates may survive; that is preferable to incorrect merges or time-consuming theorem comparisons.

One page, *Extreme value theorem*, uses the explicit heading `Proofs of the extreme value theorem`, which was identified from the article and added as a narrowly scoped anchor exception when the automatic section parser did not recognize it.

## Where links live

The generated links map is at **`data/wikipedia_proof_links.json`**, keyed by stable theorem ID. The canonical Stacks master is **not modified**. The catalog generator `scripts/publish_phase2_catalog.py` reapplies this overlay on every publication; `web/app.js` shows the links alongside existing proof references as **Link to proof (Wikipedia)**. The links are external pointers only, not proof-screening or mathematical-audit certifications.

## Files

- `REPORT.json`: machine-readable counts
- `matches.jsonl`: confirmed exact-title matches and verified proof-section fragments
- `decisions.jsonl`: classification of every accepted URL as linked or unmatched
- `unmatched_urls.txt`: retained input for later Wikipedia theorem intake

The original 1,134 accepted Wikipedia URLs and all canonical mathThm theorem content are preserved.

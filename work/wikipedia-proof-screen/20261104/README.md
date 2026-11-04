# Wikipedia proof-section structural screening — November 4, 2026

This is a deliberately **minimal, automated proof-presence check**, not a mathematical proof validation or a theorem-level equivalence check.

Input: `work/wikipedia-existing-match/20261104/unmatched_prepared.jsonl` (984 editorially prepared, currently unmatched Wikipedia theorem candidates). The previously held 137 incomplete source statements remain unchanged.

## Pass rule

For each Wikipedia article, fetch the real section index from MediaWiki and locate actual **proof-labelled headings** (e.g. "Proof", "Proofs", "Proof sketch", "Elementary proof", "Proof by induction"). Fetch the section's rendered HTML, excluding reference lists/navigation, and recognize a structurally substantive argument if it includes enough explanatory text, mathematical expressions, or both. **It does not matter whether the argument is correct, rigorous, complete, original, or really proves this theorem.** A visibly omitted proof or a short pointer to an external proof does not pass the presence check.

The script records the real proof-section anchor, heading, quantitative structure, a short diagnostic excerpt, and the specific rule that passed or failed. Mathematical review is **not performed**. It is intentionally permissive and does not disqualify truncated or mathematically invalid proofs.

## Outcomes

- `appears_to_contain_proof`: Proof-labelled section has nontrivial argument-like content; retained as a structurally screened candidate, with an unreviewed Wikipedia proof reference.
- `no_visible_proof`: No proof-labelled heading, or its content appears empty/uninformative or only points elsewhere. Held for later.
- `inconclusive`: Wikipedia API/section could not be accessed or reliably inspected. Held rather than guessing.

## Saved outputs

The one-shot GitHub Actions workflow writes `work/wikipedia-proof-screen/20261104/`:

- `REPORT.json`: aggregate counts.
- `decisions.jsonl`: one screening decision per all 984 IDs, in input order.
- `proof_screened_candidates.jsonl`: candidates that passed this **structural only** check, with a real linked section and acquisition metadata.
- `held_proof_sections.jsonl`: nonpasses/uncertainty with original editorial decisions and reasons.
- `proof_screened_urls.txt`: link list for later publication preparation.

The source statements and theorem metadata are not edited. Nothing is published during this check, and neither `data/theorems.json` nor `data/maththm_master.jsonl` is changed.

Code: `scripts/screen_wikipedia_proof_sections.py`. Tests: `tests/test_screen_wikipedia_proof_sections.py`.

Four GitHub Actions lanes independently read only their share of the 984 candidates; an exact-ID integrator checks completeness before writing result files. The temporary one-shot workflow may be removed after it succeeds.

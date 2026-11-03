# Wikipedia mathematical theorem URL triage

Purpose: Take the 2,066 original pages from the completed October 2026
English Wikipedia proof-section-heading harvest and classify each URL
as a likely mathematical theorem, unrelated, or ambiguous. No theorem
statements, proofs, or validity are examined.

**The original harvest is never changed**. All nontrivial output goes to
data/wikipedia-theorem-classification; processing code lives on
work/wikipedia-theorem-classification. A manual or one-time push-trigger
workflow is registered on main under
.github/workflows/wikipedia-theorem-triage.yml.

The workflow obtains Wikipedia category labels and up to two introductory
sentences through MediaWiki's API. Batches of ten URLs are saved to
resumable on-branch checkpoint files, with polite delays and backoff.
A source SHA-256 guard prevents accidental checkpoint reuse with different
URL data.

The classifications are intentionally conservative:

- accepted: direct theorem/lemma/mathematical-result category, or explicit
  theorem/lemma title plus mathematical context, or a clearly named mathematical
  result supported by both a mathematics category and introduction.
- rejected: explicitly unrelated subject matter with no plausible
  mathematical or theorem evidence.
- needs_review: everything else, including missing pages and unusual
  mathematical terms, so false negatives do not disappear.

**Do not assume automatic accepted results are mathematically proven, nor
that rejected pages cannot mention a theorem somewhere in their text.**
Only the topic of the article is classified. All decisions store the
category/intro signals and a reason; rejected cases remain accessible.

## Outputs

In harvest/wikipedia_classification/20261001 on the results branch:

- accepted_urls.txt
- rejected_urls.txt
- needs_review_urls.txt
- review_queue.jsonl — includes URL, title, category labels, short intro, reason
- review_worker_1.jsonl through review_worker_4.jsonl — optional collision-free
  partition of the unresolved entries for later ChatGPT review
- decisions.jsonl — all decisions with the evidence and classification
- progress.json and REPORT.md — counts and completion
- batches/*.jsonl — restartable fetched metadata
- source_manifest.json — original URL SHA-256 and immutable batch partitioning

## Run

Open Actions → Triage Wikipedia theorem URLs → Run workflow, leave
max_batches = 0 to process all remaining. GitHub Actions tests the script
before starting; it saves the completed batch results to its data branch
even if processing a later batch raises an error. Repeat to resume.
The first run is designed to process all 2,066 URLs in a few minutes to
tens of minutes, but actual API throttling and category pagination may
affect runtime. The workflow has no recurring schedule; it can be run
again intentionally when source URLs change.

Run focused offline tests from the code branch:

    python -m unittest discover -s tests -p "test_classify_wikipedia_theorem_urls.py" -v

After completion, review the ambiguity queue with ChatGPT. Accept/reject
decisions from such review should be stored separately from the automated
metadata-based decisions; no mathematical proof checking is needed.

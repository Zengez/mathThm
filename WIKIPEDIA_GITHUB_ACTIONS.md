# GitHub Actions: English Wikipedia proof-heading URL harvest

This is an independent URL discovery campaign, not part of mathThm theorem
approval or publication. It examines **English Wikipedia**, distributed free
through Wikimedia's **official enwiki dumps**. No enterprise service, trial,
secrets, or personal API keys are needed.

## Repository layout

- Crawler implementation and tests: branch work/wikipedia-theorem-harvest
- Persistent results and resumable checkpoints: branch data/wikipedia-proof-dump
- Registered workflow on main: .github/workflows/wikipedia-proof-dump.yml
- The workflow checks out the isolated code branch. No theorem records change.
- Results land in harvest/wikipedia_dump/20261001/ on the data branch.

## Run

Open **Actions → Wikipedia proof-heading URL harvest (enwiki dumps) → Run workflow**.

The initial pinned completed snapshot is 20261001, the October 2026
English Wikipedia dump (reported complete by Wikimedia on October 8).
**The October 2026 snapshot completed on November 3, 2026:** all 71
chunks, 19,314,502 main-namespace pages examined, 2,066 distinct URLs
matching the proof-heading predicate. The full run finished in about
1 hour and 42 minutes. Scheduled runs are now **disabled** to prevent
repeating this fully processed fixed snapshot. Future completed snapshots
can be started manually using Run workflow with a new YYYYMMDD date.
The default max_shards=0 scans as many chunks as fit within the
245-minute processing window (330-minute job limit); a positive limit
bounds the run for testing.

**Initial smoke test:** choose max_shards = 1 and inspect the logs, action
summary, and resulting data branch files. Offline tests run before crawling.

The code downloads the dated dump's HTML index, selects only individual
enwiki-YYYYMMDD-pages-articles-multistreamN.xml-pXpY.bz2 files, and
rejects incomplete dumps. It streams compressed XML directly without
saving large compressed files to disk.

Only main-namespace (ns=0) articles qualify. A page is accepted if its
**wikitext section heading** contains the standalone word proof or proofs,
including alternative proofs and proof sketches. This is high-recall
structural matching; template expansion is not performed, and source-only
headings can sometimes generate false positives.

## Resuming and collecting results

Each fully processed chunk produces an independent parts/<filename>.txt
on data/wikipedia-proof-dump. A part file is the completion marker;
a failed or interrupted chunk is NOT marked complete.

After each completed chunk the script regenerates:

- wikipedia_theorem_urls.txt — sorted, unique URLs, one per line
- progress.json — completed/remaining chunks and URL counts
- REPORT.md — a brief run summary
- chunk_manifest.json — the fixed list of chunks for that dump date

The workflow commits results to the data branch even when a later shard
fails, and also uploads an Actions artifact retained for 90 days.
Subsequent runs restore from the data branch, not expiring runner disk.
A concurrency lock prevents overlapping jobs from racing to update state.

The entire snapshot is finished only when progress.json shows
remaining_chunks = 0.

## Tests and limitations

Offline test command, from the isolated branch:

    python -m unittest discover -s tests -p "test_wikipedia_dump_actions.py" -v

Transient download failures are retried. If a chunk fails completely,
the job fails and future runs retry that chunk without discarding
finished work. If pushes are blocked by branch rules, review the
workflow's contents:write permission; the artifact may still contain
the completed results.

Snapshots are pinned by explicit date, not silently switched between
monthly downloads. Different dates have separate result directories.

The separate category-based API crawler in scripts/wikipedia_proof_urls.py
remains available, but is **not** automatically run by this dump workflow.
The Wikipedia-wide dump scan already covers main-namespace pages even
when their category metadata is missing or confusing. It may therefore
include non-mathematical false positives, which later workers can filter.

**No mathematical statements or proofs are extracted or validated.**
The URLs are unreviewed discovery leads only.

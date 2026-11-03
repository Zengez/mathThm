# English Wikipedia proof-heading URL discovery

This branch's discovery tool is intentionally **separate from mathThm's existing
Stacks / Stage A / Stage B / theorem-validation work**. It collects URLs only.
A matching article is **not** an approved theorem and must not be published
as one. No text, mathematical statement, proof, or source record is imported.

## Outputs

- Authoritative resumable checkpoint: .harvest_runs/wikipedia_proof/state.sqlite3
- Sorted, deduplicated URL list: .harvest_runs/wikipedia_proof/wikipedia_theorem_urls.txt
- Console progress: number of known categories, explored categories, discovered
  main-namespace pages, inspected pages, and matching pages.

The repository's existing .gitignore already excludes .harvest_runs/.
The list is regenerated atomically from the database every five discovery
iterations and at normal exit. Copy the URL file wherever subsequent workers
will read it; do **not** commit the potentially huge checkpoint database.

## First run (bounded smoke test)

Run from repository root with Python 3.10+:

~~~bash
python -m unittest discover -s tests -p "test_wikipedia_proof_urls.py" -v
python -m scripts.wikipedia_proof_urls \
  --contact "https://github.com/Zengez/mathThm" \
  --max-requests 30 --max-checks 20
~~~

Use a genuine, reachable contact email or project URL for the Wikimedia
User-Agent, not a placeholder. The default polite delay is 1.5 seconds
between HTTP requests. The smoke test uses the same database and output paths
as a larger crawl; repeat the command without budgets to resume:

~~~bash
python -m scripts.wikipedia_proof_urls \
  --contact "https://github.com/Zengez/mathThm"
~~~

The category-first pass begins with mathematical theorem/proof categories.
It explores subcategories and relevant mathematical parent categories
(bounded by --max-depth, default 9). Category membership and cursor
pagination are checkpointed; pages are queued once using MediaWiki page IDs.
Only article namespace 0 is accepted. The actual predicate is a *section
heading* containing the standalone word "proof" or "proofs", including
"Proof without Choice", "Alternative proof", and "Proof sketch".

A heading check uses MediaWiki action=parse&prop=tocdata and reads *only
the returned section headings*. It does not inspect or validate proofs.
The API may internally parse page content to generate its TOC; "headings only"
describes the information read and stored by **this** tool, not MediaWiki's
server-side processing. Apparent matches are provisional candidates.

## Exhaustive second pass (much larger)

Once category exploration yields diminishing returns, a broad pass can
enumerate *all* English Wikipedia main-namespace pages using the API.
This is potentially millions of article checks and should be run with
conservative limits/rate controls and Wikimedia infrastructure guidance:

~~~bash
python -m scripts.wikipedia_proof_urls \
  --mode allpages --contact "https://github.com/Zengez/mathThm" \
  --max-requests 1000
~~~

This **reuses the same checkpoint**. It skips articles already checked during
the category pass and adds newly matching URLs to the same output. Repeat
this command to resume with the next apcontinue cursor. Do not run multiple
processes against one SQLite checkpoint concurrently.

For an offline bulk scan instead, download an authorized English Wikipedia
articles XML dump from https://dumps.wikimedia.org/enwiki/ and run:

~~~bash
python -m scripts.wikipedia_proof_urls \
  --mode dump --dump-file /path/to/enwiki-pages-articles-multistream.xml.bz2
~~~

The dump pass checks raw wikitext heading syntax rather than the
rendered TOC. It may produce additional false positives (e.g., headings
inside commented or unrendered source). It does **not** check the mathematical
validity of the article, and is deliberately recall-oriented. This XML
streaming pass is memory bounded, but on restart it must decompress/rescan
the dump from the beginning; processed page IDs are skipped using SQLite.
This is a second-pass alternative to millions of per-page API requests.

## Useful options

- --seed "Category:Some mathematical area": additional starting category
- --max-depth 12: broaden category graph exploration
- --no-parents: follow child categories only
- --max-checks 100: stop after 100 heading checks **in this run**
- --max-requests 500: stop after 500 HTTP attempts **in this run**
- --delay 2.5: longer minimum gap between API requests
- --state PATH, --output PATH: separate independent harvests
- --progress-every N, --check-batch N: adjust reporting cadence

Requests use an identifying User-Agent, maxlag, retry/backoff on API
overload and transient HTTP failures, and MediaWiki continuation tokens.
On interruption, simply restart with the same state. The final URL list is
newline-separated, sorted by article title, and suitable as input to a
separate URL-review process.

## Tests and limitations

~~~bash
python -m unittest discover -s tests -p "test_wikipedia_proof_urls.py" -v
~~~

The offline tests exercise heading matching, URL normalization,
category/subcategory discovery, pagination, restart from SQLite state,
deduplication, and export. The code was not subjected to a large live crawl
during implementation.

Category-based discovery is not exhaustive. A proof heading is neither
necessary nor sufficient for a genuine theorem; pages without dedicated
proof headings are intentionally omitted. The global API sweep or bulk
XML dump can extend discovery to articles outside mathematics categories.

**Keep this isolated:** do not merge the generated URLs with the active
9,675 Stacks candidates or bypass their existing approval requirements.

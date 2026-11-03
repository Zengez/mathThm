# Permanent mathThm Phase 2 master — reconciliation complete

The single, materialized Phase 2 canonical master is `data/maththm_master.jsonl` (schema `maththm.master.v1`). It has **4,132 uniquely identified records**: **3,943** Phase 2 source-equivalence approval decisions and **189** holds. Records have uniform top-level keys `schema`, `candidate_id`, `source`, `formulation`, `phase2`, `phase3`, `provenance`, `publication`, and `audit`. This master is a permanent file, not an adapter over worker formats.

## One-time migration and mechanical exception reconciliation

The original migration from 3,061 frozen final-worker reviews plus 1,071 historical authoritative records is preserved in `scripts/migrate_phase2_master.py`. Its original issue report, `work/phase2-canonical-migration/REPORT.json`, is a **historical baseline**, not the current unresolved-issue count: it identified 70 distinct IDs with 77 digest/provenance flags.

Four workers independently resolved those 70 queued IDs, producing immutable, attributed `exceptions/worker-N/RESOLUTIONS.jsonl` files (22, 22, 21 and 5 records). All 70 were classified `mechanical_fix_verified`; there were no targeted mathematical holds from this reconciliation. Exact queue coverage, content identity, source transcription digests and reviewer evidence are checked before incorporation.

`scripts/reconcile_phase2_master.py` applies these decisions **once to the existing canonical master**. It preserves the original mathematical statement, all six formulation fields, all original source and reviewer snapshots, historic raw digests, Phase 2 decisions, provenance, and every publication/registration hold. Corrected canonical content hashes and independently verified Phase 3 content identity are recorded with the original hashes as forensic metadata. Each of the 70 canonical `audit.exception_resolution` objects retains its complete verified decision; there is no need for the old worker-specific schema to interpret canonical data. The summary is `work/phase2-canonical-migration/RECONCILIATION_REPORT.json`.

Run on the coordinator branch:

```sh
python -m unittest tests.test_phase2_master_migration tests.test_phase2_master_reconciliation -v
python scripts/reconcile_phase2_master.py --check
python scripts/migrate_phase2_master.py --validate
```

The one-time coordinator integration command is `python scripts/reconcile_phase2_master.py --apply`; it is idempotent, fails closed on any differing statement/digest/ID, and preserves the original evidence. The isolated GitHub Actions workflow runs this integration and commits only the canonical master and reconciliation report. **It does not run the old `--write` migration or reconstruct the file from the worker corpus.** No routine site reader should run either command. `--validate` reads the permanent master *only*, without any legacy-format adapter.

## Distinct publication gate

**Migration correctness does not imply mathematical proof verification or publication approval.** All records retain `publication.publication_ready=false`. Historical authoritative registry, current web catalog (`data/theorems.json`), `main`, and deployed site are not altered by reconciliation. Downstream admission work should read the permanent canonical master directly, run separate duplicate and publication-eligibility checks, and compare an isolated preview's candidate IDs/content before promoting anything to the live catalog.

Legacy original decision files remain in Git until the authoritative readers and publishing pipeline have deliberately been migrated; they should not be rebuilt into the master. The complete original reviews are already embedded as `audit.record_snapshots` for forensic reconstruction.

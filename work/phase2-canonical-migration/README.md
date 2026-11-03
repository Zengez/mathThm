# Permanent mathThm Phase 2 master — migration status

The canonical record file is `data/maththm_master.jsonl` (schema `maththm.master.v1`). It contains one self-contained fixed-format JSON object per candidate, sorted by candidate ID. It is **materialized once**, not produced by adapters at query time. Every record has the same top-level keys: `schema`, `candidate_id`, `source`, `formulation`, `phase2`, `phase3`, `provenance`, `publication`, and `audit`.

The migration loads exactly the 3,061 final Phase 2 review IDs from the immutable frozen allocation and all entries in the **current** authoritative registry, using exact Git blob SHA checks and ordered decision-file coverage. In the audited run, that current registry contained **1,071** historical approvals, yielding **4,132 unique master records**. The master includes 3,943 approval decisions and 189 holds; a decision is not itself permission to publish.

The `audit.record_snapshots` list retains each source Phase 2 review row in full as an opaque JSON string with its SHA-256, so no original source verdict is lost. All application-facing fields are already normalized and should be consumed **directly**. The snapshots exist solely for forensic reconstruction, not as a runtime translation layer.

Run:
```sh
python -m unittest tests.test_phase2_master_migration -v
python scripts/migrate_phase2_master.py --validate
```

The `--write` option is a **one-time** migration/rebuild tool requiring original legacy material. Do not call it from the website or normal data readers. `--validate` reads **only the permanent master**, without worker-format adapters. The GitHub Actions workflow `.github/workflows/phase2-canonical-migration.yml` executes and validates the isolated migration and commits only the master and audit report.

The existing historical authoritative registry, old worker folders, site catalog and main branch remain untouched. Source-first approval, Phase 3 cursory proof screening, proof truth verification and publication eligibility are distinct states. **All** migrated records currently have `publication.publication_ready=false`; no new authority is inferred.

The issue report is `work/phase2-canonical-migration/REPORT.json`. Exactly **70 unique candidate IDs** need targeted content-identity/provenance checks (77 flags, some overlapping); those exceptions are partitioned in `EXCEPTION_QUEUES.json`. All other records can proceed to downstream admission checks without another mathematical review, subject to duplicate checks and publication-site validation.

After resolution, coordinator tasks are: incorporate approved evidence into the permanent master, run its self-contained validator, switch authoritative/data consumers to read the canonical schema, rebuild an isolated preview site, compare all output IDs/content hashes, and only then retire original worker record files. Do not remove historical overlays until authoritative readers have been switched; Git history will retain the original source artifacts.

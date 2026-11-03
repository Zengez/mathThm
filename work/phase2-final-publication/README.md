# Canonical theorem publication (current)

`data/maththm_master.jsonl` is permanent and authoritative (4,132 records; 3,943 approved, 189 held as reconciled on 2026-11-03). Publication runs **without further content review**.

Run `python scripts/publish_phase2_catalog.py --all` to regenerate the derived `data/theorems.json`, `REPORT.json`, `BLOCKERS.json` and temporary `shards/worker-{1..4}.json`. The original 20 prototype records in `prototype_baseline.json` are required inputs and must not be deleted. Shards are deterministic throwaway outputs, not repository source files. Page deployment already runs the all-in-one publisher.

The permanent master retains individual hold reasons, IDs and source provenance; the blockers report records publication representation issues. Held candidates must remain held until individually resolved, not skipped or inferred approved.

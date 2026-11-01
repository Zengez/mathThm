# Parallel Stage B initial-pass integration audit

Date: 2026-11-01
Repository: Zengez/mathThm
Integration branch: `work/stageb/parallel-reconciled`
Pinned base: `work/stageb/parallel-base` at `f0bbfbd0951b97093c37623c1f53210a3ae9134b`
Source revision: `a04446e57ec1fbc252a871afcec7752fb2807b14`
Allocation inputs: `work/stageb-parallel/ALLOCATION.json` and immutable `READY_SNAPSHOT.json`.

## Merged worker results

| Worker | Head SHA | PR | Reviewed IDs | Preliminary approvals | Holds | Result section files | Remaining queue |
|---|---|---|---:|---:|---:|---:|---:|
| 1 | `6fa335998ca5da069e351336e3f2c269e11dc495` | #3 | 1161 | 971 | 190 | 320 | 0 |
| 2 | `f31c0f026389936f05b26adcc71a81b4a6700b49` | #4 | 1158 | 939 | 219 | 277 | 0 |
| 3 | `5ac509520342f9de216ba668be16a053bf989b26` | #5 | 1158 | 992 | 166 | 323 | 0 |
| 4 | `b4ee613562f0af37b21f15159869024a0d4d78f5` | #6 | 1157 | 964 | 193 | 324 | 0 |
| **Total** | | | **4634** | **3866** | **768** | **1244** | **0** |

## Completed integration checks

- All four remote worker queues have empty `pending` arrays after their final pushed commits.
- All four contributions descend from the same pinned base; PRs #3–#6 were merged in sequence onto this dedicated integration branch.
- Full changed-filename listings, including pages beyond the default 300-file comparison limit, contain exclusively `work/stageb-parallel/worker-N/` files for their respective worker; no shared authoritative registry, original source, scripts or other worker files changed.
- The union of result candidate IDs exactly matches the 4,634 IDs of `READY_SNAPSHOT.json.ready`: zero missing, duplicated, or unallocated IDs, checked against exclusive chapter ownership, stage-A artifact, source file, source line, section start, revision, and result file path.
- Every one of the 1,244 allocated eligible-bearing sections has a result JSONL file. Large files whose contents were omitted from GitHub PR patches were fetched and individually checked against the corresponding pinned ready-ID sets.
- All recorded decisions are either `source_equivalence_approved_pending_materialization` or `held_for_correction_or_context`. Reviewed records contain explicit reviewer identity, `source_first_review: true`, `proof_reviewed: false`, and review notes; approvals contain prepared formulation fields and holds contain hold reasons.

## What this audit does NOT do

These 3,866 positive worker decisions are **preliminary independent reviews**, not authoritative Phase 2 overlays, proof validations, or Phase 3 eligibility. The historical authoritative registry is unchanged (same Git blob SHA before and after merging). No approval is materialized in this integration operation.

Before registration, run the established `scripts/phase2_review_workflow.py` and `scripts/phase2_authoritative.py` path with explicit Stage A reconstructions, independent verdict pairs, and strict source/semantic identity, exact final formulation digests, reviewer separation, duplicate gates, and provenance checks. Hold records must remain excluded. The `READY_SNAPSHOT.json.deferred` set (4,319 entries, including previously selected / approved / malformed / non-ready cases) is a **separate final-sweep input**, not an additional set of ready first-pass approvals.

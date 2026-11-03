# Canonical mathThm migration — exception-only audit protocol

## Goal and scope
The one-time canonical master lives at `data/maththm_master.jsonl` and already contains **all 4,132** historical and final-worker candidate records with uniform fields. The four immutable exception lanes are assigned in `work/phase2-canonical-migration/EXCEPTION_QUEUES.json`. Exactly **70** candidate IDs have one or more migration flags; do not reprocess the other 4,062 candidates.

This is **primarily a metadata/content-identity audit**, not a fresh mathematical review. Existing Phase 2 reviews and provisional proof screens remain evidence. The master, historical authoritative registry, website and `main` must not be edited by exception workers.

## Assigned branches and isolation
- Worker 1: `work/phase2-canonical-exceptions/chat-1`; assigned lane 1
- Worker 2: `work/phase2-canonical-exceptions/chat-2`; assigned lane 2
- Worker 3: `work/phase2-canonical-exceptions/chat-3`; assigned lane 3
- Worker 4: `work/phase2-canonical-exceptions/chat-4`; assigned lane 4

Each worker may edit **only** `work/phase2-canonical-migration/exceptions/worker-N/`, and must commit and push completed decisions to its exclusive branch. Never mutate the global `EXCEPTION_QUEUES.json`; use a local progress file/checkpoint if useful.

## Auditing each assigned candidate ID
1. Read its canonical JSONL record (do not write another canonical schema). The canonical `audit.record_snapshots[].original_record_json` holds the complete original worker verdict as a string for forensic recovery. Inspect the pinned Stacks source, Stage B row, Phase 3 proof screen, and Phase 2 proposal only as needed to establish content identity. Do not redo proofs or source-first reviews for a purely mechanical digest issue.
2. Compare literal `statement`, `hypotheses`, `conclusions`, `logical_form`, `structured_cases`, `equivalence_sides`, candidate ID and pinned revision. Use `scripts.phase2_authoritative.content_digest` to compute the exact authoritative SHA-256 of approved content. Never reinterpret a mismatched digest as proof of mathematical equivalence.
3. For `approved_formulation_digest_mismatch`, determine how the recorded digest was calculated. If it can be reconciled without changing any reviewed mathematics, document the exact original/recomputed identities and recommend a **mechanical correction**. Otherwise hold the candidate for a targeted, independent source-first content review.
4. For `original_source_digest_mismatch`, compare raw source transcription against the pinned original, including whitespace. Classify whether this is a harmless encoding/serialization discrepancy or a substantive source mismatch. Do not silently replace source text.
5. For `phase3_reviewed_content_digest_mismatch`, investigate packed/conflated hashes and reviewed-content identity. Check whether the actual per-candidate hash and proof-screening evidence can be unambiguously linked to the approved formulation; otherwise hold for proof-screening follow-up.
6. Preserve the source, every underlying claim, and reviewer attribution. If evidence cannot be established, mark it **needs_targeted_review**, not approved.

## Fixed resolution format
Write one JSON object per assigned ID, in queue order, to
`work/phase2-canonical-migration/exceptions/worker-N/RESOLUTIONS.jsonl`.
Every record must use this uniform shape, with explicit nulls where absent:

```json
{
  "schema": "maththm.master-migration-resolution.v1",
  "candidate_id": "...",
  "worker": 1,
  "reviewer": "...",
  "source_revision": "a04446e57ec1fbc252a871afcec7752fb2807b14",
  "original_issue_types": [],
  "resolution": "mechanical_fix_verified | needs_targeted_review",
  "content_unchanged": true,
  "verified_approved_content_sha256": null,
  "verified_source_statement_sha256": null,
  "verified_phase3_content_sha256": null,
  "evidence_files": [],
  "audit_note": "...",
  "recommended_change": null
}
```

Use `recommended_change` as descriptive evidence only, **not** an automatic code patch. A `mechanical_fix_verified` means the mathematical formulation is byte-for-byte unchanged apart from provably semantics-neutral optional-field representation. Never assert mathematical correctness from a checksum.

## Completion and coordinator gate
Cover exactly your assigned IDs once each, verify no missing/duplicate IDs, check source provenance, commit/push, and report branch SHA and counts. Do not edit another lane, master records, Phase 2 authoritative registry, published catalog or site. The coordinator alone reconciles outcomes, refreshes the **single permanent master file**, reruns integrity checks, and leaves any unresolved cases unpublishable. Original legacy review files stay until that final audit and reader migration have completed.

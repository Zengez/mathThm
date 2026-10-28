# Deferred problem candidates — inherited Stacks source context

**Status:** Explicitly deferred to a later mathThm discovery phase, after the initial bulk discovery and prototype build. These are **not** rejected theorems, and they have not failed proof verification.

## Source of truth and snapshot

- [`problem_candidates_inherited_context.jsonl`](problem_candidates_inherited_context.jsonl) is the separate source-pinned registry of all currently deferred `needs_context` candidates (**862** on October 28, 2026).
- [`PROBLEM_CANDIDATES_MANIFEST.json`](PROBLEM_CANDIDATES_MANIFEST.json) contains exact batch counts, status, rebuild command, and the active-intake exclusion policy.
- Every record carries its stable `candidate_id`, original statement, Stacks source URL and pinned revision, context note, any previously recovered context, and detected references.
- Canonical, changeable Pass 2 decisions remain in `harvest/batches/<batch>/pass2.jsonl`; this registry is a **rebuildable snapshot**, not a replacement for them.

## Initial prototype / active discovery policy

1. **Exclude every record whose current canonical Pass 2 status is `needs_context`**, including every ID in this snapshot.
2. Do not treat these records as solved, as mathematical false positives, or as proof-screened.
3. Only canonical `resolved` records classified as `mathematical_result` are eligible for subsequent Pass 3 consideration; all additional review and publication gates remain in force.
4. **Do not silently change the canonical status to `not_result` or delete deferred candidates.** Their deferred status allows later recovery without reharvesting.

The independent `needs_structure` and `needs_classification` queues are *not* included in the inherited-context problem registry. The source of truth for those queues is each batch's current Pass 2 status. They require their own decisions before possible promotion.

## Future discovery

After the prototype phase, revisit the registry by candidate ID and source revision, recover inherited notation or assumptions, then replace individual Pass 2 decisions only when reliable hypothesis/conclusion structure is supported. To synchronize this snapshot with the current canonical records:

```bash
python -m scripts.pass2_problem_candidates
```

When an item is resolved later, regeneration removes it from the deferred snapshot automatically while retaining its original Pass 1 statement and updated canonical Pass 2 record. Rebuild before each new discovery tranche; older snapshots must not be mistaken for the current queue.

**Current Stacks source revision:** `a04446e57ec1fbc252a871afcec7752fb2807b14`. No proofs were opened for this archive, and the public theorem catalog was not changed.

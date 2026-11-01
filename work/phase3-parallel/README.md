# Parallel Phase 3 work — four isolated workers

Created November 1, 2026 using the completed Stage B integration at commit `fb84ebe0e2de99d12ba031f1252996d5dc8b1af2`.

The target is precisely the **3,866 preliminary Stage B source-equivalence approvals** among 4,634 reviewed candidates. The **768 held** results are excluded, as are all unrelated deferred candidates and the historical approved population. Results are partitioned by the same exclusive source-chapter ownership as Stage B; each of the **1,244 immutable section-result files** occurs in one queue only.

| Worker | Branch | Positive Stage B candidates | Section-result files | Batches |
|---|---|---:|---:|---:|
| 1 | `work/phase3/chat-1` | 971 | 320 | 34 |
| 2 | `work/phase3/chat-2` | 939 | 277 | 31 |
| 3 | `work/phase3/chat-3` | 992 | 323 | 34 |
| 4 | `work/phase3/chat-4` | 964 | 324 | 32 |
| **Total** | | **3,866** | **1,244** | **131** |

Each `worker-N/PENDING.json` has exact, pinned Git blob SHAs for every source-result file, grouped into full-section, one-chapter batches. The permitted candidate IDs are the rows in those frozen files with `decision == "source_equivalence_approved_pending_materialization"`; held rows remain excluded. Do not guess or allocate from any other source.

**Important gate:** The 3,866 are NOT currently in the Phase 2 authoritative registry. Begin materialization proposals and, where genuinely useful, *explicitly provisional* complete-proof screening. No new candidate is officially Phase 3 eligible, Pass 3 recorded, mathematically verified, or publishable unless its exact reviewed formulation is first registered by the established authoritative Phase 2 workflow and its recorded proof inspection independently passes the real Pass 3 safeguards. A coordinator will perform this registration/integration separately, without bypassing the gate.

Start an independent chat for each worker. Have it read `work/phase3-parallel/WORKER_PROTOCOL.md` and its exclusive `work/phase3-parallel/worker-N/PROMPT.md`, then immediately process its first `PENDING.json` batch. The worker's branch is based on this same pinned baseline. Source revision is `a04446e57ec1fbc252a871afcec7752fb2807b14`.

To confirm immutable inputs once on a local checkout, run `python -m scripts.phase3_parallel_preflight` (coordinator), or `python -m scripts.phase3_parallel_preflight --worker N` for a single worker. Preflight never makes mathematical judgments, reads proofs, or declares candidates authoritative.

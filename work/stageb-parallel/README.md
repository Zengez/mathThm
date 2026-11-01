# Parallel Stage B — four independent Chat lanes

Initialized 2026-11-01. Exact initial **ready-only** pool: **4634 candidate IDs** in **1244 complete candidate-bearing sections**, partitioned into **105 contiguous-section batches** across four independent workers. Each candidate appears exactly once. The immutable `READY_SNAPSHOT.json` contains the frozen ID-level eligibility audit, including separately deferred items for final sweep. Every source chapter belongs exclusively to one worker.

The pinned combined baseline incorporates (1) Stage B validation through October 31, including 1,071 authoritative approvals and all Codex selection holds; (2) all Stage A preparations on `work/phase2-stage-a-context-enrichment`; and (3) the separately completed `modules` chapter. Source revision is `a04446e57ec1fbc252a871afcec7752fb2807b14`. Do not repeat prior approvals or review holds.

| Worker | Git branch | Ready IDs | Complete sections | Batches |
|---|---|---:|---:|---:|
| 1 | `work/stageb/chat-1` | 1161 | 320 | 27 |
| 2 | `work/stageb/chat-2` | 1158 | 277 | 25 |
| 3 | `work/stageb/chat-3` | 1158 | 323 | 27 |
| 4 | `work/stageb/chat-4` | 1157 | 324 | 26 |
 
**Start:** For worker N, create a separate chat and direct it to read `work/stageb-parallel/worker-N/PROMPT.md` on its own `work/stageb/chat-N` branch, then process the first batch in `worker-N/PENDING.json`. Workers do not claim global tasks.

**Protocol:** `WORKER_PROTOCOL.md`; original ownership and counts: `ALLOCATION.json`; immutable audit: `READY_SNAPSHOT.json`. Only worker-specific results and its own pending queue are mutable. Never edit the global authoritative registry on worker branches.

**Conservative exclusions:** 416 IDs already authoritative, 128 previously selected in Codex Stage B (often holds), 399 explicitly in Stage A further-work lists, 8 unresolved canonical duplicate cases, 162 having multiple Stage A reconstructions, and 3206 not labeled ready. These disjoint counts sum to 4319; their exact IDs/reasons remain in `READY_SNAPSHOT.json.deferred`. 49 chapters have no initial ready IDs; they need not be opened by any worker in the first pass and remain assigned only for the final audit. No proof review, Phase 3 admission or publication has occurred.

# Worker 4 — independent Stage B mathematical validation

**GitHub repository:** `Zengez/mathThm`
**Work branch:** `work/stageb/chat-4`
**Exclusive queue:** `work/stageb-parallel/worker-4/PENDING.json`
**Shared rules:** `work/stageb-parallel/WORKER_PROTOCOL.md`
**Immutable candidate audit:** `work/stageb-parallel/READY_SNAPSHOT.json`

Read shared protocol and your own queue first. This queue is ALREADY fully prefiltered and allocated: **1157 exact Stage B-ready candidate IDs in 26 complete-section batches**. Start immediately with the FIRST `pending` batch, not with a repository-wide scan. Process all its candidate IDs in source order, comparing prepared statements, hypotheses and conclusions with the pinned original theorem and safe context. For additional Stacks source views use ONLY `scripts/phase2_safe_source.py` to avoid proofs/remarks; if necessary evidence is hidden, hold. Existing approvals and Codex holds are **not** in your queue.

Write independent validated-or-held result records in your exclusive `worker-4/results/<chapter>/section-<start_line>.jsonl` directory. Substantive corrections need separate later independent review and remain holds for now. For each completed full section verify exact ID coverage. Commit section results with same-commit removal of any entirely finished batch from your own `PENDING.json`. Do not change other workers' files, original sources, scripts, immutable allocation, authoritative registry or Phase 3 outputs. Push to your dedicated branch; keep going with the next batch automatically.

Per reply summarize: IDs reviewed, independent preliminary approvals, new holds, completed batches, pending batches, and last verified pushed commit. **Do not claim Phase 3 eligibility or publication.**

Start processing now; do not request manual batch assignments.

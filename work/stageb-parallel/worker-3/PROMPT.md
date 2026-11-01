# Stage B Chat worker 3

Repository: `Zengez/mathThm`. Work EXCLUSIVELY on branch `work/stageb/chat-3`. Your exclusive queue is `work/stageb-parallel/worker-3/PENDING.json`; shared immutable plan: `work/stageb-parallel/ALLOCATION.json`. Read and follow `work/stageb-parallel/WORKER_PROTOCOL.md` **before** processing candidates.

Perform a chapter-local eligibility preflight, removing already-approved IDs, all previously selected Codex Stage B IDs (including holds), Stage A further-work holds, malformed/unready reconstruction records and duplicates. Work only on your assigned chapters, one at a time, with complete consecutive sections and a running context checkpoint. **Never inspect proof material**; use only the masked pinned Stacks source viewer `scripts/phase2_safe_source.py` for additional source reads. Independently verify the math and source equivalence of the Stage A draft, including logical scope, named context, hypotheses, conclusions and quantifiers. Approve only correct already-prepared formulations as pending materialization; put substantive corrections and difficult cases on hold for a separate second review.

Write exactly one result per ready candidate into `work/stageb-parallel/worker-3/results/<chapter>/section-XXXX.jsonl`. Check section-level coverage; update your own `PENDING.json` cursor and commit together. Push to your own branch; do not modify other worker queues, global scripts, canonical source, authoritatives or shared manifests.

Continue processing as many *complete consecutive sections* as safely possible each reply. On completion, report ready candidates reviewed, preliminary approvals, holds, remaining tasks and latest verified pushed SHA. Do not stop just to ask which chapter to do next; take the next pending chapter from your queue.

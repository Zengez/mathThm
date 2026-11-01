# Parallel Stage B — November 1, 2026

Four chapter-exclusive Chat workers, backed by branches `work/stageb/chat-1` through `work/stageb/chat-4`.

The shared frozen input combines the existing Codex Stage B validation branch (1,071 authoritative approvals reported on October 31), the current Stage A preparation branch, and the separate complete `modules` chapter. The combined source tree is `02c01027bbdff09aa40dae7f38b9d983f0e67d5e`. The Stacks source revision remains `a04446e57ec1fbc252a871afcec7752fb2807b14`.

Start by pasting the contents of your worker's `worker-N/PROMPT.md` into that chat. Its exclusive `worker-N/PENDING.json` has all initial source chapters and Stage A reconstruction-file pointers. **The assignment is by chapter, not a promise that every record in a reconstruction file is eligible.** The worker filters out prior authoritative approvals, prior Stage B selections/holds, Stage A holds and incomplete drafts before working.

See `WORKER_PROTOCOL.md` for exact safe-source, checkpoint, output, and integration rules. Do not make new authoritative approvals from preliminary worker outputs until the existing independent-review materializer's checks pass.

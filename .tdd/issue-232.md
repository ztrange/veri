# Plan for #232 — push-branch.sh exits 0 on a rejected push, so a rebased run pushes nothing for its whole length and says nothing

- [x] Unreachable origin with VERI_PUSH_RETRIES=2 VERI_PUSH_BACKOFF=0: push attempted 3 times, exit 0, one stderr line naming the failure and attempt count, one push-failed event; HEAD, commit count and ledger unchanged
- [x] Unreachable origin with VERI_PUSH_RETRIES unset and VERI_PUSH_BACKOFF=0 is attempted 4 times, counted by a git stub on PATH
- [x] Origin failing the first attempt and succeeding on the second ends with exit 0, the remote branch at HEAD, and no push-failed event
- [x] Backoff is VERI_PUSH_BACKOFF seconds doubled per retry; with VERI_PUSH_BACKOFF=0 a 3-retry failure completes in under 2 s
- [x] Non-integer VERI_PUSH_RETRIES or VERI_PUSH_BACKOFF exits 2 without attempting a push
- [x] Non-fast-forward rejection (remote holds a commit the local branch amended) exits 1 after exactly one attempt, stderr carries the remote branch's full sha, and a push-rejected event records remote_sha
- [x] A successful push exits 0, writes nothing to stderr beyond git's own output, and appends no event
- [x] A failing event write (unwritable .tdd or failing event.sh) exits 2 for both an unreachable origin and a non-ff rejection
- [x] build-develop-prompt.sh reconcile renders prompts/develop-reconcile.md with the remote sha, branch and literal --force-with-lease=<branch>:<sha>, no bare --force, and exits 2 on a missing argument
- [x] classify-bail.sh reconcile-failed prints system and exits 0
- [x] SKILL.md at both push-branch.sh call sites launches develop-reconcile through supervise.sh on exit 1, bails on exit 2, requires re-running push-branch.sh and checking ledger ticks and refactor pending marks, bails with reconcile-failed otherwise, and no longer says exits 0 either way ⟂ refactor pending

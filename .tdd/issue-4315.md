# Plan for #4315 — PRD 033.2a: during an outage a reviewed run joins the local stack, gated by the full suite, with the push deferred

- [x] while `.tdd/github-outage` exists and the stack is named, `queued-merge.sh` joins onto the local stack under the merge lock (rebase, fast tier, `prose-owed.sh`, fast-forward) with no fetch, push, `gh`, `curl`, PR read, `stack-pr.sh` or `stack-red.sh` ⟦criterion 1⟧
- [x] the offline join rebases `--onto <stack> <sha>` when `.tdd/issue-<n>-base-sha` exists ⟦criterion 1⟧
- [x] with the outage file present but `.tdd/issue-<n>-base` absent, the join reads the pull request as before ⟦criterion 1⟧
- [x] an absent local `<stack>` is created at `origin/<stack>` as last fetched ⟦criterion 2⟧
- [x] a local `<stack>` that `origin/<stack>` is not an ancestor of is exit 2 naming both shas ⟦criterion 2⟧
- [x] a local `<stack>` checked out in a worktree is exit 2 naming the worktree ⟦criterion 2⟧
- [x] a `<stack>` that `refs/remotes/origin/HEAD` names as the default branch is exit 2, with no `ls-remote` ⟦criterion 2⟧
- [x] a rebase conflict, a red fast tier or a unit owing a grade is exit 1, `<stack>` unmoved, lock freed ⟦criterion 3⟧
- [x] the all-tier command runs on the rebased tip before `<stack>` moves; red is exit 1, `<stack>` unmoved, lock freed ⟦criterion 4⟧
- [x] with no all-tier command the join is not gated and says so in one stderr line ⟦criterion 5⟧
- [x] the offline cleanup removes the worktree and local branch, leaving the remote branch and `refs/veri/runs/<n>` ⟦criterion 6⟧
- [x] the tip is amended with one `Veri-Joined: <pr-url> <branch>` trailer before `<stack>` moves; exit 0 prints `joined offline, no tag` and the amended sha ⟦criterion 7⟧
- [x] a fast tier or full suite that moves or dirties the rebased tip is exit 2 with nothing amended and `<stack>` unmoved
- [ ] `stack-land.sh` exits 3 with one stderr line while `.tdd/github-outage` exists, before any read and before the lock ⟦criterion 8⟧
- [ ] the graded prose of voutage, vmerge, vdev, vhandoff and SCRIPTS.md says what VO5, VO7, M37, D69, D98, D142, D143, H10 and SC589–SC591 say, each regraded ⟦criterion 9⟧
- [ ] the logic lives in `queued_merge.py` and `stack_land.py` behind their shims and names no repository, issue, branch, label or person ⟦criterion 10⟧

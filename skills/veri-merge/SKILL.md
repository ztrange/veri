---
name: veri-merge
description: >-
  Land one finished veri run: `/veri-merge <issue-or-PR>`. Use when the user asks to merge a run's PR, cut its tag and clean up.
---

# veri-merge — land one finished run

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.

## Invocation and permission

Invoked as `/veri-merge <issue-or-PR>`; resolve the argument to the issue, its PR and its worktree.

Merging is allowed under the standing permission that `veri-dev` and `veri-coord` carry in the project repo, or under explicit permission from the user. Never merge in another repo, whatever the argument names.

## Preconditions

Merge only when all of these hold; otherwise stop and tell the human which one failed:

- The last comment on the issue is `✅ Done`.
- The committed ledger has no unchecked step and no `⟂ refactor pending`.
- Every ⟦human-owed⟧ line is ticked.
- The run did not end with an open question for the human. Merging would answer it for them, so hand the question back instead.

An unticked ⟦human-owed⟧ line gets one read-only review subagent (it may read, never write). If it answers OK, tick the line; if NOT OK, the line goes to the human and nothing merges.

## The merge lock

Take the merge lock with `$S/merge-lock.sh take --pid <driver>` before the first write and hold it to the last. `<driver>` is the long-lived process driving the merge: `$PPID` in an agent session's Bash call. Release it with `$S/merge-lock.sh release --pid <driver>` on every exit path: success, refusal, failure and interruption alike. A lock left held blocks every other merge.

The one exception: a merge that stops on a rebase conflict or a refused push leaves the lock held, and says so in its report. A human clears it with `$S/merge-lock.sh release --force` once the cause is dealt with.

## Steps

1. **Rebase if `main` moved.** Record the PR head sha, rebase onto `origin/main`, and push with `--force-with-lease=<branch>:<recorded sha>`. Never the bare `--force-with-lease`: it silently clobbers a push you have not seen.
2. **Gates.** If the repo has a `merge-gates` target, run `make merge-gates` on the rebased tip. Run `$S/prose-owed.sh <repo root>`: exit 0 means nothing owed; refuse on exit 1 (it lists units) or any other exit (no answer) (T6).
3. **CI.** Read the check rollup. An empty or missing rollup is not a pass: wait or hand it to the human, never merge on it. Wait with `$S/wait-ci.sh <pr-url> 540 "" "$(git rev-parse HEAD)"`, and call it again whenever it exits 3. The wait is capped at 2× the average duration of the last 5 runs, and never more than 10 minutes. A failure with zero steps run and a payments annotation is billing: report it to the human as billing and stop; it is not a code failure and is not retried.
4. **Merge** the PR.
5. **Read `state`.** Query the PR and continue only when `state == MERGED`. Deleting the branch, cutting the tag and removing the worktree each happen only after that read; deleting an open PR's head closes it (PR #74).
6. **Tag.** Choose the next `vN.M` from `git tag --sort=-v:refname` (never plain `sort`: lexically `v0.9` outranks `v0.10`). Cut an annotated tag whose message is the capability, in the issue's words. Push it.
7. **Clean up.** Delete the branch and remove the worktree.
8. **Release the lock** with `$S/merge-lock.sh release --pid <driver>`.

## Report

Report exactly one line: the PR url, the merge sha, the tag.

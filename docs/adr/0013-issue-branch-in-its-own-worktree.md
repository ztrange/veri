# The issue branch lives in its own worktree; the caller's checkout is never touched

Step 1 of a run no longer switches branches. `issue-worktree.sh <n> <slug>` creates — or,
being idempotent, hands back — a **linked git worktree** at `<repo-root>/.tdd/wt/<n>` with
`tdd/<n>-<slug>` checked out in it, cut from the **default** branch rather than from the
caller's `HEAD`, and prints its absolute path; the conductor `cd`s there and the whole run
happens inside it — the blind spec, the ledger, the leaf logs, every commit, the push and
the PR. The checkout `/tdd` was invoked from is left exactly as it was. If the
branch is already checked out in another worktree the script exits **2** naming that path
and touches nothing: **never steal a checkout**, because another conductor owns that run.
`--remove <n>` retires the worktree once the PR has merged, and refuses (exit 2) one
holding uncommitted changes.

## Context

`git switch -c tdd/<n>-<slug>` in place drags the invoking checkout onto the issue branch
for the whole run, and everything reading that directory follows it without being asked:
the user-level `~/.claude/skills/solve-issue` symlink into the primary clone silently
serves the run's own half-finished skill, and a dev server rooted there silently serves
the issue branch. Neither is visible from inside the run. A linked worktree is the seam
ADR-0008 already anticipated for rung 3 — a second working directory over the **one**
shared object store — so isolation and parallelism are the same mechanism, not two.
Rejected: **`git switch` in place**, for the observation above — the symlinked skill and
the dev server are the bug, not a hypothetical. **`git stash` and restore around the
run**, because the stash stack is shared across every worktree of the repo: another
session can pop the entry this run is relying on, and a crashed run leaves the user's work
stashed with no note saying so. **A fresh clone per issue**, because it discards the
shared object store (a full copy per concurrent issue) and every local branch and tag the
run may need to read, and because `origin/HEAD` is then the only default branch it can
name.

## Consequences

Rung 3 becomes possible: concurrent conductors each get their own directory, and the
never-steal refusal is what keeps two of them off one branch — an exit 2 naming the owner,
not a race. `.tdd/wt/<n>` nests under the `.tdd/` rule `ensure-run-state-ignored.sh`
already writes (#27), so the worktree is ignored by construction; git raises no objection
to a worktree living inside the ignored scratch of its own parent (verified). Preflight's
clean-tree check stays on the caller's checkout — the conductor still reads the issue and
the default branch from there, and a dirty primary means something else is mid-work — while
the worktree itself starts clean by construction. Worktrees now accumulate and must be
retired: `--remove <n>` is the `merge` skill's cleanup step, and its refusal on uncommitted
changes means a stalled run's work is never destroyed by tidying. A repo whose default
branch cannot be named (no `origin/HEAD`, no local `main`/`master`) is a **preflight-class
stop**, exit 2 — plumbing broken before any cycle, never a guess at a base.

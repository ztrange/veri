# An open PR is the claim; the pid lock is only a worktree guard

An issue is claimed when an **open pull request says `Closes #<n>`**, and by nothing else.
That is the only mark of a run every machine can see, so the conductor opens its draft PR as
the first act after the plan commit — not after the last step — and a bailed run leaves it
open. The lock `.tdd/wt/<n>/.tdd/conductor.pid` keeps its job and loses its title: it is the
**worktree guard** on the one machine that wrote it, and it claims nothing.

## Context

veri is developed from two computers, and `origin` is all they share. Until now the draft PR
was step 4 of `skills/tdd/SKILL.md`, so for the whole of a multi-step issue there was no PR
at all, and the in-flight mark was the pid lock #170 added — a number that means nothing on
any other machine. On 2026-09-14 four runs (#150, #163, #170, #174 — 71 commits) were live on
one machine that the other could not see, and `tdd/71-walkthrough-version-the-commentary-too`
sat pushed with no PR for two days, found only by a manual sweep of `origin`. A second machine
running `/tdd <scope>` would have taken any of them again. It is also the first thing that has
to hold before several development threads can run at once (#102): the claim one thread sees
must be the claim every thread sees.

The property @ztrange states for it: *a branch exists ⟹ a PR exists ⟹ it is visible and
pushed.* #191 shipped the first half (work in progress never lives only in a local branch);
this is the second.

## Decision

Two signals, two jobs, never merged:

| Signal | Scope | Job |
|---|---|---|
| open PR saying `Closes #<n>` | every machine | **claim**: the issue is out of the selection pool |
| `conductor.pid` answering `kill -0` | one machine | **worktree guard**: no second conductor enters a live worktree and `git reset --hard`s its uncommitted work (#170) |

- **A bailed run stays claimed.** Its draft PR stays open, so `solvable-issues.sh` keeps its
  issue out of the pool whether or not the pid still answers, and a scope drain never re-takes
  and re-bails it. A bail means a human needs to look; the draft PR is where they look.
  Resuming is unchanged: a human types `/tdd <n>`, which names the issue and never consults
  selection.
- **Accepted window.** Between the worktree's creation and the plan commit being pushed the
  claim is still only the local pid, because a PR needs a commit ahead of the base and the plan
  commit is the run's first. Two machines starting the same issue inside that window — the
  planning leaf's few minutes — can still collide. The PR is opened as the first act after the
  plan commit so the window is no wider than that.

### Rejected

- **A bail closes its PR.** It discards the visible record a bail exists to leave.
- **Selection reads the pid lock instead of PRs.** A pid is machine-local; claiming is a
  cross-machine problem.
- **A separate claim label or comment at launch.** It outlives a crashed run with nothing to
  clear it, and duplicates what the draft PR already records.

## Consequences

- `solvable-issues.sh` no longer treats a dead lock as a free issue. The lock frees the
  *worktree*; the PR keeps the *issue*. Its header comment and CONTEXT.md's **Solvable** entry
  both say so and cite this record.
- The draft PR exists for the whole run, so it is a live surface: each step's tick edits its
  body with the ledger's done/total count, and the final step retitles it, writes the metrics
  into it and marks it ready for review rather than creating anything.
- A resumed run edits the PR its branch already has; it never opens a second one.
- ADR-0008's "draft PR on completion" is narrowed: the PR is still a draft until the run ends
  and the human still merges, but it is opened at the start.

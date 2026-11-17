---
name: vhandoff
description: >-
  Write a session handoff so a fresh session can take over: `/vhandoff dev`. Use when the user asks to hand off, or the context is running out.
---

# vhandoff — hand a session over

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every command runs from the target repository's main working tree.

## Invocation

Invoked as `/vhandoff dev`. The role is the one argument. Resume is
`/vdev --resume <file>`.

In a session that has the app's `start_session` tool (the desktop app), `/vhandoff dev` writes
nothing: say that the dev session resets itself and recovers from its role state file
(`.tdd/role-dev.state`), and stop. In a session without it (a terminal), it works as below.

## Refusals

For the dev role, refuse, say which, and write nothing while:

- `$S/merge-lock.sh holder` names a live holder (a stale lock, whose holder is gone, does not refuse);
- a launch is half done (a worktree or claim exists without its conductor running).

Wait for it to finish, then retry.

## Writing it

Write to `.tdd/handoff-<role>.md` in the main clone, never `/tmp` or a scratch dir (they
vanish mid-run). Read state from `$S/status.sh` and git; do not recall it from memory.

It carries, and only this:

- the time, and the main sha and tag;
- live conductors: issue, step k/n, phase, cost;
- parked runs, each with its reason;
- PRs awaiting merge;
- N, and any timed change to it;
- for overrides and one-off permissions, a pointer to the role state file
  (`.tdd/role-<role>.state`), where they are written (P9); copy none of them here;
- pending decisions;
- whether `.tdd/github-outage` exists in the main working tree, read from the file
  when the handoff is written, and, when it does, each PR url it lists, in the file's order:
  the `mode on|off` and `held <url>` lines `$S/github-outage.sh status` prints.

It carries no rule the role's skill already states (P2): the resuming session reads that skill.
State only what is true now.

Keep it to 40 lines or fewer. Every item names its issue number and title, as `#<n> <title>`.

## What it must not do

It stops no conductor. Conductors are detached and outlive both sessions; leave them running.

## Finish

Print the resume command in a fenced block, with the real file path:

```
/vdev --resume .tdd/handoff-dev.md
```

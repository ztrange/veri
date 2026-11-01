---
name: vhandoff
description: >-
  Write a session handoff so a fresh session can take over: `/vhandoff dev|coord`. Use when the user asks to hand off, or the context is running out.
---

# vhandoff — hand a session over

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every command runs from the target repository's main working tree.

## Invocation

Invoked as `/vhandoff dev|coord`. The role is the one argument. Resume is
`/vdev --resume <file>` for dev, or `/vcoord --resume <file>` for coord.

## Refusals (dev only)

For the dev role, refuse, say which, and write nothing while:

- `$S/merge-lock.sh holder` names a live holder (a stale lock, whose holder is gone, does not refuse);
- a launch is half done (a worktree or claim exists without its conductor running).

Wait for it to finish, then retry. The coord role has no such refusal.

## Writing it

Write to `.tdd/handoff-<role>.md` in the main clone, never `/tmp` or a scratch dir (they
vanish mid-run). Read state from `$S/status.sh` and git; do not recall it from memory.

It carries, and only this:

- the time, and the main sha and tag;
- live conductors: issue, step k/n, phase, cost;
- parked runs, each with its reason;
- PRs awaiting merge;
- N, and any timed change to it;
- overrides and one-off permissions, each with its expiry;
- pending decisions.

It carries no rule the role's skill already states: the resuming session reads that skill.
State only what is true now.

Keep it to 40 lines or fewer. Every item names its issue number and title, as `#<n> <title>`.

## What it must not do

It stops no conductor. Conductors are detached and outlive both sessions; leave them running.

## Finish

Print the resume command in a fenced block, with the real file path:

```
/vdev --resume .tdd/handoff-dev.md
```

(or `/vcoord --resume .tdd/handoff-coord.md` for coord).

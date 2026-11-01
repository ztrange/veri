---
name: vstop
description: >-
  Stop veri's conductors without losing work: `/vstop`. Use when the user asks to stop, pause or wind down a run.
---

# vstop — stop runs without losing work

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.

## Invocation

Invoked as `/vstop [<issue>|--all] [ledger|leaf|now]`. The first argument names the run to
stop: one issue number, or `--all` for every running conductor. The second is the grade, and it
defaults to `ledger` when omitted. `$S/stop-run.sh --mode` accepts `at-ledger`, `at-leaf` and
`now`, so each grade maps to the mode it accepts:

- `ledger` — `--mode at-ledger`: the default.
- `leaf` — `--mode at-leaf`.
- `now` — `--mode now`.

Never pick a harsher grade than the user asked for.

## After each conductor exits

Nothing may exist only locally. Once a conductor has exited, check its worktree and show the
user all three:

- a clean tree (`git status --porcelain` is empty);
- an empty `@{u}..HEAD` (`git log @{u}..HEAD` lists no commit, so nothing is unpushed);
- a committed ledger (the ledger file has no uncommitted change).

Then report where each run would resume: the issue, and the step and phase the next
`run-conductor.sh` would pick up from the committed ledger. A check that fails is reported as
failed, never smoothed over.

## What it is not for

It is never used to lower N (P8). Stopping a run is not a way to reduce how many conductors
run at once; that is set by the concurrency principle, not by this skill.

# TDD Issue-Solver Framework

A Claude Code skill suite that solves GitHub issues by strict TDD/XP discipline.
A conductor drives one issue at a time through Red → Green → Refactor cycles,
spawning supervised `claude -p` leaf subprocesses, with independent agents
verifying that each test genuinely fails and genuinely passes. _(Name provisional.)_

## Language

**Conductor**:
The orchestrator that drives one GitHub issue end-to-end — sizing it, planning it,
and running its TDD cycles by launching leaves. One conductor per issue.
_Avoid_: orchestrator (ok as a gloss), driver, runner

**Leaf**:
A single `claude -p` subprocess that performs exactly one step (e.g. write the failing
test, implement, refactor) and then returns. Leaves never persist across steps.
_Avoid_: subtask, worker, job

**Supervisor**:
The helper script every leaf is launched through. It watches the leaf's heartbeat
(progress-log activity) and a hard timeout, and kills + retries/escalates a leaf that
hangs or goes silent. No leaf is ever launched directly.
_Avoid_: monitor, watchdog (watchdog ok as a gloss)

**Independent Verifier**:
A leaf whose sole job is to confirm a claim made by a *different* leaf — that a test
genuinely fails for the right reason, or genuinely passes — without having authored the
test or the code. It is **blind** (given only the test, the issue spec, and the repo —
never the author's rationale) and establishes ground truth itself by **running the test**.
_Avoid_: checker, reviewer, validator

**Verdict**:
A verifier's structured output: `PASS` or `REJECT` plus a reason. The conductor branches
on the verdict; a `REJECT` carries the reason that feeds the revision.
_Avoid_: result, status

**Heartbeat**:
The signal the supervisor uses to tell "slow but working" from "hung" — activity on the
leaf's progress log within a window.
_Avoid_: ping, pulse

## Scope ladder

The framework grows in three rungs, each wrapping the previous — never a rewrite:

1. **Single issue** — solve one GitHub issue end-to-end.
2. **Loop** — run the single-issue conductor across all open issues, one after another.
3. **Parallel** — run several issue-conductors at once, solving issues concurrently.

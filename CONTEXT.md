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

**Issue thread**:
The GitHub issue's comment stream, used as the framework's observability channel — the
conductor posts the plan, per-cycle outcomes, and the final result/bail there. It is the
canonical human-facing record of a run.
_Avoid_: log, comments (as the canonical record)

**Attempt budget**:
The capped number of revise attempts the conductor will make against a `REJECT` verdict
(default 2) before bailing the issue and escalating. Distinct from the supervisor's
stuck-retry budget.
_Avoid_: retries (unqualified)

**Plan**:
The conductor's decomposition of an issue into a checklist of small steps, each a single
TDD cycle's worth and aligned to an acceptance criterion. It is looped to completion.
Sizing is surfaced here, not enforced as a gate.
_Avoid_: TODO list, backlog

**Ledger**:
The local, committed file (one per issue) that holds the plan as a checkbox list and is
the **source of truth** for which steps are done. Committed atomically with each cycle's
code; the issue thread mirrors it. Resume reads the ledger for the next unchecked step.
_Avoid_: TODO.md (it generalizes that), state file

**Acceptance criterion**:
A condition from the issue that must hold for the issue to be considered done. The plan's
steps map to criteria; the conductor loops until all are covered.
_Avoid_: requirement, spec (unqualified)

**Issue branch**:
The per-issue git branch (`tdd/<issue>-slug`) all of an issue's commits land on. On
completion it is pushed and a draft PR (`Closes #<n>`) is opened for human review. In v2
each issue branch lives in its own git worktree so parallel conductors don't collide.
_Avoid_: feature branch (ok as a gloss)

**Cycle**:
One Red→Green→Refactor pass over a single plan step. Structure: red (developer writes one
failing test) → verify-red (blind) → green (developer writes minimum impl) → verify-green
(blind) → green commit → refactor loop (one behavior-preserving transformation per leaf,
suite-gated, until none remain) → verify-refactor (blind, once) → refactor commit.
_Avoid_: iteration, round

**Triangulation**:
Forcing a general implementation by adding successive failing tests for further cases,
rather than hand-writing generality. The only sanctioned route to general code here.
_Avoid_: parameterization (unqualified)

**Dependency marker**:
A reference in a GitHub issue declaring that it depends on another issue. An issue is
**solvable** only once its dependencies are closed. The dependency graph is the
eligibility signal for automated issue selection in later rungs (preferred over a
hand-applied label).
_Avoid_: blocker (ok as a gloss), prerequisite

## Scope ladder

The framework grows in three rungs, each wrapping the previous — never a rewrite. Issue
selection changes per rung; everything below the selection layer stays the same:

1. **Single issue** — the human names the one issue to solve (`/solve-issue <number>`). XP:
   point it at exactly one, no automated selection yet.
2. **Loop** — run the single-issue conductor across all *solvable* issues (dependencies
   closed), one after another.
3. **Parallel** — run several issue-conductors at once over the solvable set, respecting
   the dependency graph, solving issues concurrently.

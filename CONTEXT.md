# veri

A Claude Code skill suite that solves GitHub issues by strict TDD/XP discipline.
A conductor drives one issue at a time through Red → Green → Refactor cycles,
spawning supervised `claude -p` leaf subprocesses, with independent agents
verifying that each test genuinely fails and genuinely passes. The name comes from
that blind independent verification — the core that sets veri apart from the
reference suite it grew out of.

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
The per-issue git branch (`tdd/<issue>-slug`) all of an issue's commits land on. It lives in
its own **worktree** at `.tdd/wt/<issue>`, made by `issue-worktree.sh` and cut from the
default branch, and the whole run happens in there — so the **caller's checkout** is never
switched onto it and two conductors never collide. On completion the branch is pushed and a
draft PR (`Closes #<n>`) is opened for human review.
_Avoid_: feature branch (ok as a gloss)

**Worktree**:
A linked git working directory — a second checkout sharing the one `.git` object store —
that an issue branch lives in, at `.tdd/wt/<issue>` inside the target repo. One per issue,
created (or, idempotently, handed back) by `issue-worktree.sh` and removed by its
`--remove <n>` once the PR merges; removal refuses a worktree with uncommitted changes. A
branch already checked out in another worktree is never taken over — another conductor owns
that run.
_Avoid_: workspace, sandbox, clone (it is not one — the object store is shared)

**Caller's checkout**:
The working directory `/solve-issue` was invoked from. The conductor reads the issue and the
default branch there and then moves into the issue's worktree; it is never switched, never
committed in, and never left changed by a run. Anything reading that directory — a skill
symlinked out of it, a dev server serving it — therefore keeps seeing what it saw before.
_Avoid_: primary clone (ok as a gloss — it usually is that, but need not be), host repo

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

**Bail**:
The conductor's terminal stop on an issue it cannot complete. It preserves completed
commits, pushes the branch, posts a diagnostic comment that classifies the cause as a
**system failure** (plumbing broke) or a **process failure** (methodology spoke), and
opens no PR. Re-running resumes from the ledger.
_Avoid_: abort, fail (unqualified)

**Pin**:
A step outcome for a criterion that earlier work already satisfies: the developer leaf's
honest test passes against the unmodified code. Instead of verify-red (which can only
reject a passing test) the conductor runs **verify-pin**, a blind check that the test
passes now, *fails* under a behaviour-removing mutation the verifier applies and reverts
itself, and is behaviour-level. On `PASS` the test lands as a `test:` commit with the
ledger tick atomic, narrated as `📌 Already satisfied`; Green and Refactor are skipped.
_Avoid_: characterization test (ok as a gloss), skip, no-op step

**Dependency marker**:
A reference to another issue under a GitHub issue's `## Blocked by` heading, declaring
that it depends on that issue. An issue is unblocked once every issue named there is
closed; a section reading `None.` names none. The dependency graph is the **ordering**
signal for automated issue selection — what may go next — while the `ready-for-agent`
label is the **eligibility** signal, the human's explicit opt-in.
_Avoid_: blocker (ok as a gloss), prerequisite

**Solvable**:
The property that makes an issue veri's to take right now: it is open, carries the opt-in
label, every issue under its `## Blocked by` heading is closed, and no open pull request
already says `Closes #<n>` for it (such a PR means a run is in flight, or one bailed and
left the branch behind). All four hold at once or the issue is not solvable. Solvable is
therefore relative to *one* label: `VERI_LABEL` names it and `ready-for-agent` is only the
default, so the same issue can be solvable for one loop and invisible to another. That is
the intended use — **one label per loop** when more than one loop runs against a repository,
partitioning the backlog into disjoint pools rather than having both take the lowest number
off one list.
_Avoid_: eligible, ready, available, unblocked (that is only one of the four)

**Selection layer**:
The part of veri that decides *which* issue is next, and the only part that changes per
rung of the scope ladder. Everything below it — conductor, leaves, supervisor, blind
verification, ledger — is identical at every rung. At rung 2 it is `solvable-issues.sh`,
which prints the solvable numbers ascending (exit 3 when there are none).
_Avoid_: scheduler, picker, queue

## Scope ladder

The framework grows in three rungs, each wrapping the previous — never a rewrite. Issue
selection changes per rung; everything below the selection layer stays the same:

1. **Single issue** — the human names the one issue to solve (`/solve-issue <number>`). XP:
   point it at exactly one, no automated selection yet.
2. **Loop** — `/solve-issues` runs the single-issue conductor across the *solvable* issues,
   one after another, recomputing the solvable set after every issue rather than walking a
   list captured once. The first bail stops the loop unless told otherwise. It adds no
   failure mode of its own: every outcome is one of rung 1's.
3. **Parallel** — run several issue-conductors at once over the solvable set, respecting
   the dependency graph, solving issues concurrently.

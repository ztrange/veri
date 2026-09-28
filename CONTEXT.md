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
code; the issue thread mirrors it. A step's green commit ticks it and marks it
`⟂ refactor pending` in the same write, and that mark comes off only when the step's
verify-refactor passes — so a tick alone says green, not tidied. Resume reads the ledger
for the next unchecked step.
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
The working directory `/tdd` was invoked from. The conductor reads the issue and the
default branch there and then moves into the issue's worktree; it is never switched, never
committed in, and never left changed by a run. Anything reading that directory — a skill
symlinked out of it, a dev server serving it — therefore keeps seeing what it saw before.
_Avoid_: primary clone (ok as a gloss — it usually is that, but need not be), host repo

**Cycle**:
One Red→Green→Refactor pass over a single plan step. Structure: red (developer writes one
failing test) → verify-red (blind) → green (developer writes minimum impl) → verify-green
(blind) → green commit → refactor (one refactor leaf for the whole step: it applies the
touched files' structural candidates up to `VERI_REFACTOR_BUDGET`, suite-gated, and commits
each transform itself, after which the conductor checks what it left) → verify-refactor
(blind, once). ADR-0017 records that shape; it supersedes ADR-0010.
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
label, every issue under its `## Blocked by` heading is closed, and nobody has claimed it.
All four hold at once or the issue is not solvable. The claim is an open pull request saying
`Closes #<n>` — the one mark of a run every machine can see, since veri is developed from more
than one computer and `origin` is all they share. The conductor opens that draft PR as the
first act after its plan commit, so it stands for the whole run rather than for its last
minutes, and a bailed run leaves it open: the issue stays claimed until a human looks, which is
what a bail is for. The lock `.tdd/wt/<n>/.tdd/conductor.pid` is not a second claim but the
worktree **guard**, and only on the one machine that wrote it: while the pid in there still
answers `kill -0`, no second conductor there may enter that live worktree and `git reset
--hard` the running leaf's uncommitted work away (#170). A pid is meaningless on any other
computer, so a lock nobody answers for frees the *worktree* and never the *issue*. ADR-0024
records the division of labour and the three claims rejected for it. Solvable is
therefore relative to *one* label: `VERI_LABEL` names it and `ready-for-agent` is only the
default, so the same issue can be solvable for one loop and invisible to another. That is
the intended use — **one label per loop** when more than one loop runs against a repository,
partitioning the backlog into disjoint pools rather than having both take the lowest number
off one list. The print order — `priority`, then `bug`, then the rest — runs over the set the
four conditions leave and never enlarges it: a `priority` or `bug` issue that is blocked,
claimed or not carrying the opt-in label is still not printed, because a band says *sooner*
and only `VERI_LABEL` says *at all*.
_Avoid_: eligible, ready, available, unblocked (that is only one of the four)

**Selection layer**:
The part of veri that decides *which* issue is next, and the only part that changes per
rung of the scope ladder. Everything below it — conductor, leaves, supervisor, blind
verification, ledger — is identical at every rung. At rung 2 it is `solvable-issues.sh`,
which prints the solvable numbers of one scope in three bands — the issues labelled
`priority` first, then the `bug`s, then the rest, each band ascending by number (exit 3 when
there are none). `VERI_PRIORITY_LABEL` names the first band's label.
_Avoid_: scheduler, picker, queue

**In flight**:
A conductor one `parallel-conductors.sh` invocation launched and has not yet seen finish.
The set is local to one invocation: it lives in the launcher's own memory, is subtracted
from what `solvable-issues.sh` prints before each launch, and nothing outside the invocation
can read it. Two launchers on one label still collide — each sees only its own — which is
why the answer stays one label per launcher; across machines the claim is the draft PR
(ADR-0024), not this set. ADR-0025 records why it is not written anywhere.
_Avoid_: running (a leaf runs too), claimed (a claim is the PR)

**Scope**:
The pool one `/tdd <scope>` invocation drains: the issues carrying that scope's opt-in
label. `plain` is the default scope and is the bare `ready-for-agent` label; any other
scope is `ready-for-agent:<scope>`. One scope per loop — two loops on one scope collide.
_Avoid_: pool, queue, label (as the user-facing name)

**Worker**:
A named, long-lived session that drains its own items of the work queue one at a time —
`next`, `start`, run the conductor, then `done` or `park` — until `next` finds nothing
launchable. It keeps the judgement calls (merging, reading a bail); the queue's state
changes are `workqueue.sh`'s. The loop it follows is `skills/tdd/WORKER.md`.
_Avoid_: thread (ok as a gloss), leaf, actor

**Work queue**:
The file `.tdd/workqueue` in the main working tree, written only by `workqueue.sh`, that
assigns issues to workers in order and records what became of each: one line per item,
`<worker>	<issue>	<state>	<detail>`, with `state` one of `queued`, `running`, `merged`,
`parked`, `skipped`. Lines are never deleted, so it is also the record of what each worker
did, and no issue is `queued` or `running` for two workers at once. Local to one machine,
like the conductor's pid lock; it does not decide what is assigned — that is the selection
layer's job.
_Avoid_: handoff, backlog, scope (a scope is a label's pool, not an assignment)

**Bug**:
A kind of issue, marked by the `bug` label, reporting behaviour the code has and should
not: what happened, what was expected, and how to get there. A scope's bugs are taken
before any of its other issues, and a bug's Red is a **reproduction**.
_Avoid_: defect, hotfix, regression (for the issue — that is the test's word)

**Reproduction**:
The Red of a bug: one test that encodes the expected behaviour and fails on the current
code **for the reported reason** — not for a missing symbol or a typo, which the blind
verifier rejects. Once Green it stays as the bug's regression test.
_Avoid_: repro (ok as a gloss), failing test (unqualified)

**Actor**:
One of the three things that act in a run: the conductor, a developer leaf, a verifier
leaf. The scripts the conductor runs are not actors; what they do is recorded as the
conductor's events.
_Avoid_: agent (ok as a gloss), worker, process

**Event log**:
The per-run, append-only record of what each actor did and when: every leaf launch, exit
and verdict with its wall time, turns, tokens and cost, and the conductor's step, pin, bail
and completion marks. It is what every viewer and every metric reads. It is not the human
record — that stays the issue thread.
_Avoid_: trace, telemetry, audit log

**Attempt**:
One leaf launch in service of a phase. A step's attempts are its first leaf plus every
revise after a `REJECT` and every stuck retry.
_Avoid_: try, iteration, retry (unqualified — that is the supervisor's word)

**Rework**:
What a step spent on attempts that were `REJECT`ed before it recovered and reached Step
done — their time, tokens and cost, counted per phase. Kept apart from waste: rework
bought the step, waste bought nothing.
_Avoid_: waste, retries

**Waste**:
Everything a bailed step spent. The bail reverts the step's uncommitted work, so every
attempt in it — including phases whose verdict was `PASS`, such as a Red that passed
before Green bailed — bought nothing. Committed earlier steps are never waste.
_Avoid_: rework, loss, cost (unqualified)

**Metrics**:
The per-issue summary computed from the event log: attempts, verdicts, kills, rework and
waste per phase and per step; wall time, tokens and cost per step and in total; steps done
of planned. Committed beside the ledger and posted with the run's final comment. A scope's
metrics are the sum over its issues' and are never committed.
_Avoid_: stats, telemetry, report

**Entry point**:
A place veri is invoked from by name: a script invocation in `SKILL.md`, a Makefile target,
or a git hook. Its command-line contract is fixed, so a refactor keeps it byte-identical and
moves what is behind it. Functionality reachable from no entry point is dead. ADR-0026.
_Avoid_: main, public API

## Scope ladder

The framework grows in three rungs, each wrapping the previous — never a rewrite. Issue
selection changes per rung; everything below the selection layer stays the same:

1. **Single issue** — the human names the one issue to solve (`/tdd <number>`). XP:
   point it at exactly one, no automated selection yet.
2. **Loop** — `/tdd [<scope>]` runs the single-issue conductor across the *solvable* issues
   of one scope,
   one after another, recomputing the solvable set after every issue rather than walking a
   list captured once. The first bail stops the loop unless told otherwise. It adds no
   failure mode of its own: every outcome is one of rung 1's.
3. **Parallel** — run several issue-conductors at once over the solvable set, respecting
   the dependency graph, solving issues concurrently. `parallel-conductors.sh` is its
   selection layer, and `/tdd <scope>` runs it when `VERI_PARALLEL` is above 1: rung 2's
   loop, keeping up to that many supervised print-mode conductors **in flight** and
   re-selecting after each one finishes. ADR-0025 records the design.

---
name: vjudge
description: >-
  Decide a veri question the way the owner would, or surface it to them only when their principles
  do not settle it: `/vjudge <the question>`, or `/vjudge`. Use before any operator session
  (coordinator, dev session) asks the human anything — a ruling, an option menu, a "should I".
---

# vjudge — decide like the owner, ask only what is not clear-cut

Alias: `/vjudge`

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

The owner's principles, mined from their rulings and corrections across every veri session. Most
questions an operator session wanted to ask were already answered by one of them — the most
frequent replies on record are "go with your recommendation", "agree all", "why did you ask
again?". This skill turns such a question into a decision you make and state, and keeps the
human's attention for the questions where their principles pull apart or the call is theirs by
nature.

## The procedure

Run it on every question before it reaches the human.

1. **Is it an operation, not a decision?** Opening or updating a PR, filing, commenting on or
   closing an issue, editing repo files, running tests, removing a run's own files, re-arming a
   watcher, a `gh` command: do it and report it (P14). Never phrase an operation as a question,
   and never offer an "(a) do it / (b) hold" menu. A merge is not one of these: it follows
   `vmerge` and the caveat rule — every caveat the review found goes to the coordinator, and
   the merge waits for a reply that names each one.
2. **Is it on the always-surface list below?** Then surface it (step 5), whatever the
   principles seem to say.
3. **Run it through the principles, J1 to J12.** Name every principle that applies and what each
   says to do.
4. **They agree, and the choice is reversible inside the project repo** → it is clear-cut.
   Decide, act, and report it in one line that names the principle and the alternative not taken:
   `Decided: hand-fixed the missing case on the branch (J1: close the loop); not a follow-up issue.`
   Reversible means a later run or a revert undoes it without loss; a merge to the default branch
   that CI and review passed counts.
5. **They disagree, the material difference is money or a guarantee, or step 2 matched** →
   surface it, once, in the format below.

When unsure whether a case is clear-cut, it is not: surface it. A wrong guess on a tension costs
more than one question; a question the principles answer costs the owner's attention and has
been corrected every time.

## The principles

Each is a rule, what it decides, and the call it overrode when an agent guessed differently.

**J1 — The feedback loop is as close and quick as possible.** A gap a review finds is fixed on the
PR's branch before merge, never filed as a follow-up. A refactor is done in the issue that found
it or dropped; never a "refactor owed" issue. Obsolete tests are retired in the same change that
makes them obsolete, not batched to the end of a plan. *Overrode:* merge now plus a follow-up
issue; retiring tests in one sweep at the end.

**J2 — Tests are fast, and the bar does not move.** The fast tier's target, as the target
repo's CLAUDE.md or the human's standing rules state it, stands; a slow test means missing
dependency injection, not a looser target. Work that makes every future run faster or cheaper
outranks ordinary bugs. CI jobs keep tight timeouts, raised only on evidence of cancelled runs.
*Overrode:* relaxing a stated target because it was hard to reach ("why are you so insistent to
lower the bar?"); a CI cap looser than the jobs needed.

**J3 — Cheapest tier that does the job, proven by measurement.** A cheaper model, runner or
design is tried and kept if a blind evaluation shows the quality loss is below the saving.
Recurring spend is cut at the source and never widened silently. A park costs nothing, so a
tighter budget ceiling beats a split or a bigger ceiling. *Overrode:* keeping a costly CI runner
for a narrower trigger instead of dropping it; a ceiling well above the run's projected cost; a
recurring check that real runs already replace.

**J4 — Use the capacity, pace the week.** Weekly usage is paced at the daily rate the human's
standing rules set. Before a reset, unused capacity is waste: fill the slots. N is lowered by not refilling, never by killing
a run. Another model's bucket is not extra capacity when it counts toward the all-models limit.
*Overrode:* moving work to a "free" model bucket; leaving capacity unspent before a reset.

**J5 — veri fixes veri.** A defect in veri's product code becomes an issue veri runs, not a hand
fix — even a bug that blocks veri itself: it is filed through `vfile`, and the run it stopped
takes the normal bail handling. The only hand fix is a test-only gap on a run's branch, and it
simulates TDD: failing test first, go-red check, blind review. *Overrode:* a hand-built
PR ("why did you fix it instead of creating an issue?").

**J6 — Fix the rule, not the instance.** When a rule forces the same bail or exception on more
than one issue, the rule (ADR, prompt, requirement) is changed through an issue; no per-issue
exemption. The same defect across several runs gets one general issue. *Overrode:* exempting one
issue from an ADR that would trip the next wave.

**J7 — Behaviour, not metrics or wording.** An acceptance criterion is a behaviour "pinned by a
case". Timings and sizes go in the PR body via measurement, never in criteria. Full coverage is
not a goal of TDD: a surviving mutant is a PR-body note, except in a guard, an exit-code path, or
code that deletes or overwrites. Prose is verified by graded requirements, never by a stronger
substring pin. *Overrode:* a mutation-audit phase; "2 s" as a criterion; hand-strengthening a
string pin.

**J8 — Diagnose, measure, then decide.** Find where the problem really lies and what it costs
before choosing a fix; question every requirement's necessity ("why would we need root?").
Ask "why" before dropping something. *Overrode:* a gate proposed before checking whether
the full suite already catches the defect.

**J9 — Smallest scope that works, then iterate.** Do what was asked, not the fuller fix. The
simplest reversible version first. A PR that keeps failing review is split, not fought. A
thought the owner says aloud is not an instruction. *Overrode:* a full hook rework where a notice
was asked for.

**J10 — Keep moving.** Slots stay full while the queue is not empty; a stalled run is a defect.
A death from a usage limit, network outage or machine sleep is resumed, not counted as a bail.
Environment churn (tool updates, sleep) is absorbed: veri is made resilient, the environment is
not asked to hold still. *Overrode:* asking to pause tool updates; waiting for an OK to re-arm.

**J11 — The queue's natural order rules.** The order is the selection layer's. Blockers express
dependency; the priority label the target repo's CLAUDE.md names is proposed only for work that
makes future runs cheaper or faster, with the saving in one line. *Overrode:* the priority label
used to sequence work that a blocker line already orders.

**J12 — State lives where the next reader finds it.** A park is a label plus a comment saying
why; a claim is a label; a decision is in the issue or commit body. Never local memory alone.
Deterministic mechanisms over clever ones. Docs lag development and never block it.

## Always surface

These are the owner's by nature, or were decided case by case on record. Surface them even when
a principle seems to answer them.

- **Money past a standing rule**: a budget ceiling above the one-resume raise, N above the
  current cap, any new recurring spend (runner, cron, paid API), a bigger CI runner.
- **Product direction**: the next PRD or milestone, a PRD's shape, dropping or keeping a platform
  or a dependency rule, closing a PRD, opening a lane.
- **Weakening a guarantee the owner asked for**: merging with a criterion gap, accepting a
  narrower fix than the issue states, relaxing an ADR or a requirement row.
- **What becomes of a parked run**: the dev session resumes a first bail once and parks a
  second, with one issue comment giving the cause and what would unblock it; it never asks.
  Whether a parked run on product code is resumed with a raised budget, merged as is or closed
  is the human's, surfaced by the coordinator from that comment.
- **Preempting a running run** to land another issue sooner.
- **A first-of-kind precedent**: the first run of a new kind of change, whose review sets the
  bar for the ones after it.
- **Requirement rows for a graded unit**, and any change to them.
- **Deleting code whose only caller is its own test**, or functionality no one calls.
- **Anything outside the project repo, a push to the default branch, a machine or security
  setting, the repository's visibility or ruleset.**
- **Two principles in material tension**, typically: J2 or J3 (speed, cost) against a
  guarantee (coverage, a review bar); J1 (fix on the branch) against J5 (veri fixes veri) when
  the fix touches product code; J4 (use capacity) against J3 (cheapest tier) for a costly run.

## Surfacing a decision

Once, when it arises, in full (P4), and never again on routine events:

- **What is decided**, in one sentence, naming the issue or PR and what it is.
- **Why it is not clear-cut**: the principles that pull apart, or the always-surface item it is.
- **The options**, each in words with its cost (money, time, a guarantee given up).
- **The recommendation**, and the principle it leans on.

No option letters without their words, no pointer to an earlier message, no "reply a/b/c".
While it waits, keep every other thread moving (J10).

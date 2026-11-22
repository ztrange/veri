---
name: vish
description: >-
  Develop under TDD discipline without a veri run: find the suite, prove it green, plan the
  change as small behavioural steps, then run Red → Green → Refactor per step — the red predicted
  before it is run and watched to fail for the right reason, the green the minimum the test demands,
  the refactor bounded to the files that cycle touched. Use when the user says "tdd", "vish", "use
  TDD", "test-driven", "test first", "write the test first", "red green refactor", "do this
  test-first", "start with a failing test", or asks for a change to be developed test-first. One
  worktree, no state machine; the main thread orchestrates and every suite run and cycle happens in
  a subagent, so test output never grows the main context — for the changes where a veri run is not
  worth its weight. When the request names a GitHub issue, it claims the issue with veri's label and
  ticks a veri-format plan ledger as steps land.
---

# vish — TDD discipline, nothing around it

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <resolved base dir> rev-parse --show-toplevel`); read it first.

Installed user-level, this skill's base directory is a symlink, and `<base dir>/../` does not
reach veri through it. Resolve it first, `cd -P <base dir> && pwd`, and use that resolved
directory, `<resolved base dir>`, everywhere below, never the path the harness reports. `$S` is
`skills/tdd/scripts/`, reached as `<resolved base dir>/../tdd/scripts/`.

**Run veri's scripts from the project worktree**: they read the repository from the current
directory.

**You run in the user's own session, so your questions go straight to the user, never through
`vjudge`** (P22's exception).

**The rigour lives in the order of operations and in what each phase is allowed to touch, not in
machinery.** There is no blind verifier and no bail/revise loop.

**The project wins on convention.** Its runner, its test layout, its naming, its assertion style.
This skill supplies the loop, never the stack.

## Who does what

Every subagent below follows the rules of this section. Test output, file dumps and build logs are
what fills a TDD session's context; none of it belongs in the main thread.

| Main thread | Subagent |
|---|---|
| Picks the test commands, claims the issue (*Before the first cycle*), writes the plan and ledger (*Plan the change as behavioural steps*) | Runs the baseline (*Before the first cycle*) and the closing full suite (*Closing the change*), returns counts and failing case names |
| Hands one step to a cycle agent, reads its report, decides go/split/drop/stop | Runs one step's Red → Green → Refactor (*The cycle*) in the worktree |
| Verifies narrowly: `git log --oneline -3`, `git show --stat HEAD`, the predicted vs observed red quoted in the report | Reads the code, writes the test and the production code, runs the suites |
| Ticks the issue's acceptance criteria, pushes, opens the PR | — |

- **Always, even for a one-line step.** A run of small steps done inline is exactly how the main
  context grows unnoticed.
- **One cycle agent per step, sequentially, in the one worktree** — no isolation, no parallel
  cycles. Two cycles in parallel would write the same files and break "one writer per worktree".
  While one runs, the main thread does not edit.
- **The cycle agent commits locally, never pushes.** The step commit and each refactor commit are
  the cycle's atomic units, and routing each one back through the main thread costs a round trip
  per transform. Push and PR stay with the main thread.
- **Same step, same agent.** A split, a re-prediction or a "go ahead with Refactor" goes back by
  `SendMessage` to the agent that already holds the test in its context, not to a fresh one.
- **Model**: the cycle agent runs on the session's model (it writes code you will not re-read); the
  baseline and full-suite runners run on the cheapest model that can do it, `haiku` (they only
  count), and return counts and the names of failing cases only.
- **Every subagent brief keeps all writes in the project repo**, and says that a fix belonging in
  another repository is reported — repository, file, the change — and not made.

The cycle agent's brief is self-contained, since the agent knows only what it is given. It carries,
pasted: the repo and worktree path, the step's criterion verbatim, the narrow and full test
commands, the ledger path and line if any, the commit-subject convention, and *The cycle* of this
file by path (`<resolved base dir>/SKILL.md`, `## The cycle`) as its rules. Its return, at most 20 lines:

```
step: <criterion>
red: predicted <failure|error: message> / observed <failure|error: message> — match|diverged
green: <covering suites run> → <pass/fail counts>
commits: <sha subject> per commit, step commit first, refactor commits after
reverted: <transform, why> or none
owed: <overfit noted for a later step> or none
stop: <why the user is needed> or none
```

A `stop`, a `diverged` it could not resolve, or a red that passed comes back to the main thread
as a decision — the agent does not drop, split or re-phrase a step on its own.

## Before the first cycle

1. **Name the test commands out loud, and say where they came from.** Read them with
   `$S/detect-test-command.sh --tier fast`, `--tier all` and `--tier "one test file"`: the root
   `CLAUDE.md` lines `veri: fast tests:`, `veri: all tests:` and `veri: one test file:`, then
   inference from the repo's files. **An exit 3 for the fast or all tier → ask**, never guess. A
   guessed command that runs a subset looks exactly like a green suite. An exit 3 for the
   one-file tier means the repo states no `veri: one test file:` line: the narrow command is then
   derived from the runner, as *Red* says.
2. **Claim the issue, when the request names one**, with `$S/unlabel-issue.sh <n>` — when that
   issue's baseline (item 3) starts, never ahead. It swaps the opt-in label (`$VERI_LABEL`, default
   `ready-for-agent`) for `taken:<lane>`, so veri's `solvable-issues.sh` stops listing it.
   - **Exit 2 naming the missing opt-in label → no claim**: say so and carry on; the issue is not
     this skill's to take.
   - **Exit 2 naming another lane's `taken:` label → stop and ask**: an issue already taken by
     another lane is someone else's run.
   - **Exit 2 naming this lane's own `taken:<lane>`, with the ledger `.tdd/issue-<n>.md` present →
     a resumed hand run**: that refusal is the expected answer; carry on without claiming again.
   - **On a claim, it also posts or updates the issue's `### 📍 Run state` comment**, whose
     `Resume:` line names `$S/run-conductor.sh <n>`. Say so when you report the claim, and that no
     conductor is running: the issue is in development by hand.

   **`taken:<lane>` means in development.** Under a concurrency cap, an issue waiting for a slot
   stays on the opt-in label; "claim them all" means take each as a slot frees. An issue whose PR
   waits to merge keeps `taken:<lane>` until the merge closes it, but does not count against the
   cap. An unstarted claim is released by swapping the two labels back on the issue;
   `$S/release-issue.sh` releases only a parked or bailed issue.
3. **Run the all-tier suite before changing anything**, in its own worktree and branch, through a
   subagent that returns counts and the names of failing cases only. A red baseline is a finding,
   not a starting point: report which cases fail and ask whether to repair them first; no step is
   developed on it. Developing on a red suite means no phase below can tell its own failure from
   the inherited one.

## Plan the change as behavioural steps

Write the steps where the user can see them — the task list, or the draft PR body.

**When the request names issue `<n>`, the plan is also a ledger**, `.tdd/issue-<n>.md`, in the
format `skills/tdd/SKILL.md` *2. Scope & plan → the ledger* defines (`<resolved base dir>/../tdd/SKILL.md`),
so a veri run could resume the same branch:

```
# Plan for #<n> — <issue title>

- [ ] <behaviour, one cycle's worth> ⟦criterion k⟧
- [ ] <a gap step no acceptance criterion covers>
```

`k` is the 1-based position of the checkbox in the issue's `## Acceptance criteria` it serves; a
gap step carries none. Commit it before the first Red: `plan: scope #<n> into <k> steps (#<n>)`.
`.tdd/` is often gitignored — `git add -f .tdd/issue-<n>.md`. No issue → no ledger.

**Once every step carrying `⟦criterion k⟧` is ticked**, the main thread — never a cycle agent,
since it writes to GitHub — ticks the k-th checkbox under the issue's `## Acceptance criteria`
with `$S/tick-issue-criterion.sh <n> <matcher>`.

- **Each step is one externally observable behaviour**, phrased as the criterion a test will pin:
  "rejects a payload whose `amount` is negative", not "add validation" and not "write the validator
  class". If you cannot say what would be observed, it is not a step yet.
- **Smallest step that is still a behaviour.** A step whose Red needs three new collaborators is two
  steps.
- **A step that turns out too big mid-cycle gets split**, not pushed through. Reset the uncommitted
  work, replace the step with the smaller ones, say so, continue.

## The cycle

Per step, in this order: Red, Green, Refactor; the next step's Red starts only after this step's
Refactor. This section is the cycle agent's rulebook; "you" below is that agent.

### Red

**One failing test, no production code.**

- **Exactly one new test case**, pinning this step's criterion and nothing else.
- **Behaviour, not mechanism.** Assert what the caller observes. No call counts, no private-field
  reads, no timings — a test that describes the implementation breaks on the refactor it was meant
  to protect.
- **No production code in this phase.** Not a stub, not a signature, not an empty class to make the
  import resolve. **The subject not existing yet is a legitimate red** — `ImportError: cannot import
  name 'split_cents'` is this step's failure, reported by most runners as an *error* rather than a
  failure. Predict which of the two you will get; "1 error" where you predicted "1 failure" is a
  divergence like any other.
- **Predict the failure first.** Before running, state what you expect to see — which assertion,
  which message, failure or error. Then run only the suite holding the case, against unmodified
  code. **That narrow command is usually not the all-tier one**, a whole-suite invocation whose
  flags may not even be legal on the single-module form (`python3 -m unittest discover -s tests -t
  .` → `python3 -m unittest tests.test_split`). Use the `veri: one test file:` command when the
  repo states one, else derive it from the runner; a run that dies on its own arguments has told
  you nothing.
  - **It failed as predicted** → Green.
  - **It failed differently** → your model of the code is wrong. Read, do not patch. Fix the
    understanding, re-predict, re-run. A red you did not predict is worth more than a green.
  - **It failed by accident, not by the criterion** — a typo, a missing fixture, an import naming
    the wrong module, a bad command line → that is not this step's red. Fix it and run again. The
    test is `assert`ing nothing yet, so this costs only a re-run; mistake it for the red and you
    commit a green that was never earned.
  - **It passed** → the criterion is already satisfied by code that exists. **Do not weaken the test
    to make it fail.** Either the step is redundant (say so, drop it) or the criterion was wrong
    (re-phrase it and start the Red again).
  - **It cannot be pinned as a lightweight behavioural test at all** → say so and stop for the user.
    A criterion is not re-phrased into whatever happens to be testable.
- **Keep it cheap and self-contained.** Costly dependencies replaced unless the behaviour under test
  *is* the dependency; the case never runs another suite and never re-runs its own.

### Green

**The minimum that passes.**

- **The least production code that turns that case green.** No generality the test does not demand,
  no error handling nobody asked for, no second case handled in advance.
- **"Least" means the simplest code that expresses the criterion, not the shortest text that
  satisfies the assertion.** For "splits 900 three ways into [300, 300, 300]", that is
  `[total // ways] * ways` — not `return [300, 300, 300]`, which passes, is genuinely smaller, and
  pins nothing. A constant return is not a step; it buys a cycle of ceremony and leaves the next
  test to do all the work. Write the obvious implementation of *this* criterion and let it stay
  wrong for the criteria no test has stated yet.
- **No test file is edited in this phase.** Editing the test in Green moves the goalposts; if the
  test is genuinely wrong, go back to Red and say why.
- **Run the suites covering what you changed**, not just the one case. A green case over two reds
  elsewhere is not a green step.
- **Commit here, one commit per step**, with the criterion in the subject — `feat: rejects a
  negative amount`. This is the step's atomic unit: before this commit the step does not exist, and
  after it the behaviour is pinned.
- **With a ledger, tick the step in this same commit** with `$S/tick-ledger.sh <ledger> <matcher>`,
  never in a commit of its own.

### Refactor

**Bounded, behaviour-preserving, separately committed.**

- **Bounds are the source files this cycle touched.** `git show --name-only HEAD` is the list, minus
  what is not code — the step commit may also carry a config file, a fixture, a lockfile. Tidying
  outside that list is a different change and belongs in a different PR.
- **Structural before cosmetic**, and cosmetic usually not at all: a duplicated branch, a name that
  lies, a seam missing where the step kept reaching through — those pay. Reformatting does not.
- **One commit per transform**, `refactor: <what>`, so a break stays attributable.
- **Run the covering suites after every transform.** Red → **revert that transform**, do not chase
  it green. A behaviour-preserving change that changes behaviour was not the refactoring you
  thought it was.
- **No test file is edited in this phase.** Touching a test here removes the only thing checking the
  refactor; a test that is genuinely wrong goes back to Red, with the reason said.
- **Generality comes only from triangulation.** Overfit code — a hardcoded return, a special case
  the one test happens to accept — is not hand-generalized here. Either the next step's test forces
  it, or you note it as owed and move on. A general implementation nothing tests is worse than an
  obvious special case.

Then back to the next step's Red.

## Closing the change

- **Run the full suite**, not the narrow one, before pushing — through a subagent, counts only.
  Report the counts.
- **A step you dropped, split or could not test is named in the PR body** with why — the plan was
  visible, so its deviations are too. With a ledger, the same goes for an unticked line.
- Branch → push → draft PR. **This skill never merges.**

Before the PR is marked ready, the break and the mutation runs below, each through a subagent that
returns one line per criterion or mutant. A step's Red only proved its test fails against code that
did not exist yet; these prove the finished code is pinned.

- **Break each acceptance criterion's behaviour.** For each acceptance criterion of the issue,
  break the behaviour in the product code, never the test, run the criterion's test and watch it go
  red, then restore the product code and see it green again. **A criterion whose test stays green
  is not done**: strengthen its test, back to Red with the reason said, or report the criterion as
  unpinnable.
- **Mutate each guard, exit-code and delete path the change added**: a condition inverted, an exit
  code swapped, a deletion skipped, one mutant at a time, the covering suites run after each, the
  code restored after each. **Every mutant that survives**, the suites still green, gets a test that
  fails on it, through a Red of its own.
- **The PR body lists, per acceptance criterion, the test that pins it** (`file::case`) **and that
  it was watched red** by the break above, alongside the deviations and the full-suite counts.

Mark the PR ready only once every criterion's test went red, no mutant survives, and the body says
so.

## What it does not do

veri's `/tdd` (`skills/tdd/`) does all of this and carries, additionally: a conductor process
driving subagent leaves, blind verification of every phase by an agent that never saw the author's
reasoning, the ledger as the run's source of truth (resume, refactor-pending marks), an event log
with per-step cost budgets, a bounded revise loop with bail causes, and GitHub-issue orchestration —
issue comments per phase, a WIP draft PR opened at plan time, metrics. **None of that is here, and
`vish` never starts a veri run and never merges.** Borrowed, and only when the request names an
issue: the claim label and the ticked ledger — written for the user and for a later veri run,
never read back by this skill.

That machinery buys verification you cannot rubber-stamp and a run that survives its own
context; it costs a worktree per issue and a lot of leaf-seconds.

The subagents here are not that: the main thread hands work to them to keep its context small, not to get
an independent check, and it hands each cycle agent the plan it wrote.

So the honest trade this skill makes: **the cycle agent checks its own work.** The prediction step
in Red is the cheap stand-in — a red you called in advance is harder to fool yourself with than one
you rationalize afterwards — and it is not equivalent. When the change is load-bearing enough that
self-verification is not good enough, use veri, or ask a fresh subagent for a second opinion, given
the test and the criterion, never the reasoning.

## When TDD is not the right loop

Say which of these applies rather than performing the cycle hollowly:

| Situation | Instead |
|---|---|
| Exploring an unfamiliar API | Spike first, throw it away, *then* step 1 |
| A pure refactor, no behaviour change | There is no red to write. Prove the behaviour is covered first — mutate the code you are about to move and watch the suite go red — then transform |
| Config, docs, dependency bump | No test to write. Say so |
| A bug with no reproduction | The reproduction *is* the red. Write it before touching anything |

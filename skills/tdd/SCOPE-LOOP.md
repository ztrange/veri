# tdd — draining a scope

The other half of the `tdd` skill. `SKILL.md` is resident in every conductor request; this
file is not — it is read only when `## Inputs` resolves the argument to a **scope**, which is
a branch a single-issue run never takes. `$S` and every script, budget and role named below
are `SKILL.md`'s, and you have already read them by the time you get here.

## Draining a scope — the loop

`SKILL.md`'s *Procedure* drives **one** issue. A **scope** asks instead for a drain: the same
single-issue procedure, run repeatedly, wrapped in a loop whose only new job is
**selection** — deciding which issue is next and when to stop. This is rung 2 of the scope
ladder, and it lives here rather than in a second skill so the selection layer and the
scripts it calls are one thing; its steps are numbered `Loop 0`–`Loop 5` because they are
its own sequence, not the *Procedure* steps in `SKILL.md`.

Everything below the selection layer is unchanged, and **the loop adds no new failure mode
of its own**: every outcome of it is one of rung 1's outcomes (draft PR, or a bail
classified system or process), and the committed ledger makes any interrupted run resumable
by re-invoking the same command.

**You never merge anything.** Each solved issue ends on a draft PR for a human, exactly as
rung 1 leaves it.

### Loop inputs

- `$ARGUMENTS` may carry `--continue-on-bail` (or the user may say "keep going past
  bails") — see *Loop 4*. It may also carry `--repo <owner/name>` to select a repository
  other than the current one; pass it straight through to `solvable-issues.sh`.
- `VERI_MAX_ISSUES` — a cap on how many issues one invocation will attempt. Read it as
  `${VERI_MAX_ISSUES:-0}`; **0 means no cap**, which is the default, because the solvable
  set is finite and the `ready-for-agent` label is already the human's opt-in. Set it when
  you want a short, watchable run.
- **The scope's selection label**, derived from the scope's own word: the scope `plain`
  drains the bare `ready-for-agent` label — every issue opted in today carries that, so the
  bare invocation keeps draining them — and any other scope `<s>` drains
  `ready-for-agent:<s>`. That colon is the namespacing which lets **one label per loop** be
  the rule without anyone spelling a label: `/tdd docs` and `/tdd scripts` draw from
  disjoint pools instead of racing for the same issues. `solvable-issues.sh` knows nothing
  of scopes — it reads a label from the environment — so deriving it is yours: put the
  derived label in `VERI_LABEL` before *Loop 1* calls it.
- `VERI_LABEL` — an **override** of that derivation, so the label this loop drains is
  `${VERI_LABEL:-<the scope's label>}`. It is read by `solvable-issues.sh`, so pass it
  through the environment rather than as an argument. Set, it **moves** the gate, it does
  not widen it: the pool becomes exactly the issues carrying that name, whatever the scope
  derived — which is what a launcher needs when the pool it wants is one no scope word
  spells. Two loops given the *same* value still collide; that is the human's choice. Set
  but empty is refused with exit 2 rather than matching every issue.

### Loop 0. Preflight — none of its own

Do **not** duplicate the *Procedure*'s preflight. The first single-issue run performs it
(git repo, clean tree, `gh` and `claude` authenticated, suite green at baseline, default
branch captured), and a poisoned baseline makes that run refuse to start before any branch
or cycle exists. That refusal is a bail like any other, so it stops the loop here too —
with nothing done and nothing to revert.

### Loop 1. Select

```
$S/solvable-issues.sh [--repo <owner/name>]
```

It prints the numbers veri may take right now, one per line, ascending; **exit 0** when
there is at least one, **exit 3** with empty stdout when there is none.

- **Exit 3:** report `nothing solvable` and stop, **naming the label you drained** —
  `${VERI_LABEL:-<the scope's label>}`, as in `nothing solvable under ready-for-agent:docs`. A
  loop that says `no ready-for-agent issue` while it was launched on another label sends
  the reader to the wrong list. Not an error — no issue is open, carrying that label,
  unblocked and unclaimed. Nothing was started.
- **Exit 0:** take the **first** number. Do not keep the rest of the list. The order is
  banded — `priority`, then `bug`, then the rest, each ascending — so the first number is
  not always the lowest one. When it is not, **say so and name the band that did it**:
  `#220 (priority) before #108`, `#120 (bug) before #117`. A jump is otherwise invisible in
  the report — a number that jumped a lower-numbered issue reads exactly like one that came
  up next — and the operator who labelled it an hour ago cannot tell the label was read.

### Loop 2. Solve one issue

Run `SKILL.md`'s *Procedure* for that number end to end — its preflight, branch, ledger, cycle
loop, bail semantics and draft PR, unchanged and un-second-guessed. You are the same agent;
the run happens wherever that procedure puts it, so do not relocate it or invent a branch of
your own.

Record its outcome: the **PR url**, or the **phase and classification** of its bail.

### Loop 3. Re-select, do not walk the list

After each run, go back to **Loop 1** and run `solvable-issues.sh` again. Never continue
down the list you printed last iteration — it is stale. The issue you just solved now has
an open PR saying `Closes #<n>`, which removes it from the set, and closing its
dependencies may have **unblocked others** that were not solvable a moment ago. The list
is recomputed every iteration; that is the whole of the loop's state.

### Loop 4. Stop conditions

Stop and report when any of these holds:

- **A bail.** The first bail — **system or process, either one** — stops the loop, unless
  the user passed `--continue-on-bail` or said to keep going past bails. In that case
  record the bail and continue at *Loop 1*; the bailed issue leaves a pushed branch and no
  PR, so it stays in the solvable set and would be retried immediately — **skip it** for
  the rest of this invocation rather than re-running it.
- **A stop.** The issue just run ended in a stop. The loop reports and stops: it does not
  go back to *Loop 1*, and it does not select another issue. Unlike a bail, a stop has no
  `--continue-on-bail` equivalent: a stop is the operator speaking, and the loop has no
  business overruling it. Re-invoking the same command resumes the stopped issue from its
  committed ledger — the single-issue resume, no new machinery — and then carries on
  draining the scope.
- **An empty list.** `solvable-issues.sh` exits 3 — the drain is complete.
- **The cap.** `${VERI_MAX_ISSUES:-0}` is non-zero and that many issues have been
  attempted. Say the cap stopped the loop and that re-invoking the same command continues.

### Loop 5. Report

One line per issue attempted, in the order attempted:

```
#<n> — <PR url> | bailed: <phase> (<system|process> failure) | stopped: <mode> | skipped: <why>
```

Then one line naming **what stopped the loop**: the bail, the stop and the stopped issue's
mode, the empty list, or the cap. If
a run was left mid-issue, say that re-invoking the same command resumes it from its
committed ledger — no step is repeated and none is skipped.

### Loop guardrails

- **The loop adds no new failure mode.** Every outcome is one of rung 1's. If you find
  yourself inventing a state this loop can be in, you are doing rung 1's job over again —
  don't.
- **Never merge, and never mark a draft PR ready.** A human lands the code.
- **Never hand-pick an issue** that `solvable-issues.sh` did not print, and never re-order
  the ones it did. The `ready-for-agent` label is the opt-in and `## Blocked by` is the
  ordering; neither is yours to override.
- **Recompute, never cache.** The stale-list bug is the one mistake available here.
- **Do not touch a bailed issue's branch.** It is pushed and diagnostic; the human reads
  it, or a later single-issue run resumes it from the ledger.

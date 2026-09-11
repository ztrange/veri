---
name: solve-issues
description: >-
  Drain every solvable GitHub issue — open, opted in with `ready-for-agent`, unblocked,
  and not already claimed by an open PR — by running the `/solve-issue` conductor over
  them one at a time, recomputing the list after each run and stopping on the first bail.
  Leaves one draft PR per solved issue and never merges. Invoke as `/solve-issues`. Use
  when the user wants veri to work through the solvable backlog rather than one named
  issue.
---

# solve-issues — the veri loop

You are the **conductor**, run repeatedly. This is rung 2 of the scope ladder: the same
single-issue procedure as `/solve-issue`, wrapped in a loop whose only new job is
**selection** — deciding which issue is next and when to stop. Everything below the
selection layer is unchanged, and **you add no new failure mode of your own**: every
outcome of this loop is one of `/solve-issue`'s outcomes (draft PR, or a bail classified
system or process), and the committed ledger makes any interrupted run resumable by
re-invoking `/solve-issues`.

**You never merge anything.** Each solved issue ends on a draft PR for a human, exactly as
rung 1 leaves it.

## Locating the scripts

Let `S=<base directory>/../solve-issue/scripts`, where *base directory* is the path the
harness printed when this skill loaded (`Base directory for this skill: …/solve-issues`).
The selection layer is `/solve-issue`'s script, not this skill's — this skill ships no
scripts. The sibling path holds in both installations: in the repo the two skills sit side
by side under `skills/`, and installed they sit side by side under `~/.claude/skills/`.
Both must be installed; if `$S/solvable-issues.sh` is not there, say so and stop.

## Inputs

- `$ARGUMENTS` may carry `--continue-on-bail` (or the user may say "keep going past
  bails") — see *Stop conditions*. It may also carry `--repo <owner/name>` to select a
  repository other than the current one; pass it straight through to
  `solvable-issues.sh`. No arguments is the normal case.
- `VERI_MAX_ISSUES` — a cap on how many issues one invocation will attempt. Read it as
  `${VERI_MAX_ISSUES:-0}`; **0 means no cap**, which is the default, because the solvable
  set is finite and the `ready-for-agent` label is already the human's opt-in. Set it when
  you want a short, watchable run.
- `VERI_LABEL` — the opt-in label this loop drains, `${VERI_LABEL:-ready-for-agent}`. It is
  read by `solvable-issues.sh`, so pass it through the environment rather than as an
  argument. Setting it **moves** the gate, it does not widen it: the pool becomes exactly
  the issues carrying that name and `ready-for-agent` stops being special, which is the
  point — **one label per loop** is how two loops on one repository draw from disjoint
  pools instead of racing for the same issues (say, `ready-for-agent:docs` for one and
  `ready-for-agent:scripts` for the other). Two loops given the *same* value still collide;
  that is the human's choice. Set but empty is refused with exit 2 rather than matching
  every issue.

## Procedure

### 0. Preflight — none of your own

Do **not** duplicate `/solve-issue`'s preflight. The first `/solve-issue` run performs it
(git repo, clean tree, `gh` and `claude` authenticated, suite green at baseline, default
branch captured), and a poisoned baseline makes that run refuse to start before any
branch or cycle exists. That refusal is a bail like any other, so it stops the loop here
too — with nothing done and nothing to revert.

### 1. Select

```
$S/solvable-issues.sh [--repo <owner/name>]
```

It prints the numbers veri may take right now, one per line, ascending; **exit 0** when
there is at least one, **exit 3** with empty stdout when there is none.

- **Exit 3:** report `nothing solvable` and stop, **naming the label you drained** —
  `${VERI_LABEL:-ready-for-agent}`, as in `nothing solvable under ready-for-agent:docs`. A
  loop that says `no ready-for-agent issue` while it was launched on another label sends
  the reader to the wrong list. Not an error — no issue is open, carrying that label,
  unblocked and unclaimed. Nothing was started.
- **Exit 0:** take the **first** number. Do not keep the rest of the list.

### 2. Solve one issue

Invoke the `/solve-issue` procedure for that number: you are the same agent, so this
means following that skill's SKILL.md end to end for `<n>` — its preflight, branch,
ledger, cycle loop, bail semantics and draft PR, unchanged and un-second-guessed. The run
happens wherever `/solve-issue` puts it; do not relocate it or invent a branch of your
own.

Record its outcome: the **PR url**, or the **phase and classification** of its bail.

### 3. Re-select, do not walk the list

After each run, go back to **step 1** and run `solvable-issues.sh` again. Never continue
down the list you printed last iteration — it is stale. The issue you just solved now has
an open PR saying `Closes #<n>`, which removes it from the set, and closing its
dependencies may have **unblocked others** that were not solvable a moment ago. The list
is recomputed every iteration; that is the whole of the loop's state.

### 4. Stop conditions

Stop and report when any of these holds:

- **A bail.** The first bail — **system or process, either one** — stops the loop, unless
  the user passed `--continue-on-bail` or said to keep going past bails. In that case
  record the bail and continue at step 1; the bailed issue leaves a pushed branch and no
  PR, so it stays in the solvable set and would be retried immediately — **skip it** for
  the rest of this invocation rather than re-running it.
- **An empty list.** `solvable-issues.sh` exits 3 — the drain is complete.
- **The cap.** `${VERI_MAX_ISSUES:-0}` is non-zero and that many issues have been
  attempted. Say the cap stopped the loop and that re-invoking `/solve-issues` continues.

### 5. Report

One line per issue attempted, in the order attempted:

```
#<n> — <PR url> | bailed: <phase> (<system|process> failure) | skipped: <why>
```

Then one line naming **what stopped the loop**: the bail, the empty list, or the cap. If
a run was left mid-issue, say that re-invoking `/solve-issues` resumes it from its
committed ledger — no step is repeated and none is skipped.

## Guardrails

- **The loop adds no new failure mode.** Every outcome is one of `/solve-issue`'s. If you
  find yourself inventing a state this loop can be in, you are doing rung 1's job over
  again — don't.
- **Never merge, and never mark a draft PR ready.** A human lands the code.
- **Never hand-pick an issue** that `solvable-issues.sh` did not print, and never re-order
  the ones it did. The `ready-for-agent` label is the opt-in and `## Blocked by` is the
  ordering; neither is yours to override.
- **Recompute, never cache.** The stale-list bug is the one mistake available here.
- **Do not touch a bailed issue's branch.** It is pushed and diagnostic; the human reads
  it, or a later `/solve-issue <n>` resumes it from the ledger.

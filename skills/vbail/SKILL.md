---
name: vbail
description: >-
  Handle a run that exited without finishing: `/vbail <issue>`. Use when vdev sees any exit that is not ✅ Done.
---

# vbail — decide what a failed run gets

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every command runs from the target repository's main working tree, except the save and restore in
the run's worktree `.tdd/wt/<n>`.

## Invocation

Invoked as `/vbail <issue>`. `vdev` calls it on every exit that is not ✅ Done.

## Classify first

Classify from facts before acting, never from the wording of the bail comment. Name one source
per class. First run `$S/stop-reason.sh <issue>` from the target repository's main working
tree and read its first line:

- `running`: the run is live; take no action.
- `done <pr>`: not a bail; take no action.
- `stopped <mode>`: a requested stop, not a bail; report the mode and take no action.
- `usage-limit [<reset text>]`: a usage limit (see below).
- `bailed <phase> <classification>`: classify by the bail event, next.
- `killed [<text>]` or `unknown [<text>]`: a sleep (see below) when a `gap <ts> <ts>` line
  follows (two consecutive events more than `VERI_SLEEP_GAP` seconds apart); otherwise ask
  the human.

Exit 2 is no answer: classify nothing, take no action, and report stop-reason's stderr.

On `bailed …`, read the `cause` of the last `bail` event in `.tdd/wt/<n>/.tdd/events.jsonl`
and label it with `$S/classify-bail.sh <cause>`; check its answer against the ledger,
`$S/status.sh`, the logs and git:

- `killed-stuck`: killed-stuck;
- `no-verdict`: the no-verdict budget;
- `step-too-big`: the step-growth budget;
- `revise-exhausted`: revise-exhausted (`REVISE_BUDGET`, or a ⟦skill-edit⟧ step's budget);
- `needs-user` with `classification` `process`: a ledger question. Quote it from that run's
  `### ⛔ Bailed — <phase> (process failure)` comment and take it to the coordinator or the
  human (see Budgets and ledger);
- `needs-user` with no `classification` field: the conductor stopped unmarked (a red baseline
  or any other preflight stop, with the issue comment `needs-user: the conductor stopped
  without a verdict.`). No source tells these apart, so ask the human which;
- any other cause: a real bail of that cause and its classify-bail category.

## A usage limit or sleep is not a bail

In the run's worktree `.tdd/wt/<n>` (the only place this save and restore happens), save every
uncommitted leaf edit, untracked files included, as a binary-safe patch under `.tdd/`
(`git add -A && git diff --cached --binary HEAD > <file>`, then `git reset`), and restore that
worktree's tree to the last commit (`git reset --hard && git clean -fd`). When usage is back,
re-apply the patch in that worktree with `git apply <file>`, then resume. It spends no resume
and costs no park.

## A first real bail: resume once

Resume the run once with `$S/detach-leaf.sh $S/run-conductor.sh <n>`, run from the target
repository's main working tree. If the fix it needs
landed after the commit recorded in `.tdd/issue-<n>-skill-commit`, set `VERI_NEW_SKILL=1`
on that resume so it re-pins the skill; otherwise resume as it was.

## A second bail: park

If the run has already been resumed once and bails again, park it. Post one issue comment
with the cause and what would unblock it, then take the next issue.

## Budgets and ledger

Raise a budget or amend the ledger only on the coordinator's or the human's word, never on
your own. The change applies to that one resume and is not kept.

A ledger step amended in place between runs, on that word, is committed with a `plan: rewrite`
subject. That commit becomes the growth baseline `ledger-growth.sh plan-sha` reads; under a
plain `plan:` subject the reworded step reads as a new line with no `⟦added⟧` record, and the
resumed run bails `step-added-off-route`.

## What it must not do

It leaves the run's logs in place: it deletes none of them.

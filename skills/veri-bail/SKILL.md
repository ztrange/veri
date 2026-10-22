---
name: veri-bail
description: >-
  Handle a run that exited without finishing: `/veri-bail <issue>`. Use when veri-dev sees any exit that is not ✅ Done.
---

# veri-bail — decide what a failed run gets

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every command runs from the target repository's main working tree.

## Invocation

Invoked as `/veri-bail <issue>`. `veri-dev` calls it on every exit that is not ✅ Done.

## Classify first

Classify from facts before acting, never from the wording of the bail comment. Read the
ledger, `$S/status.sh`, the run's events and logs, and git. Pick one:

- usage limit;
- sleep;
- killed-stuck;
- a budget (name which: stuck, no-verdict, revise, refactor, step growth, skill edit);
- revise-exhausted;
- red baseline;
- a ledger question.

`$S/classify-bail.sh <cause>` labels a cause; check its answer against the facts.

## A usage limit or sleep is not a bail

Save any uncommitted leaf edit as a patch under `.tdd/` (`git diff > <file>`), restore the
tree to the last commit, and resume when usage is back. It spends no resume and costs no
park.

## A first real bail: resume once

Resume the run once. If the fix it needs landed after the run launched, set
`VERI_NEW_SKILL=1` on that resume so it re-pins the skill; otherwise resume as it was.

## A second bail: park

If the run has already been resumed once and bails again, park it. Post one issue comment
with the cause and what would unblock it, then take the next issue.

## Budgets and ledger

Raise a budget or amend the ledger only on the coordinator's or the human's word, never on
your own. The change applies to that one resume and is not kept.

## What it must not do

It leaves the run's logs in place: it deletes none of them.

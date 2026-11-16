---
name: vjudge
description: >-
  Decide a question the way the owner would, from rules mined from the owner's own overrides,
  and hand the owner only what is theirs by nature: `/vjudge <the question>`, or `/vjudge`. Use
  before any operator session asks the human anything — a ruling, an option menu, a "should I".
---

# vjudge — decide like the owner, surface only what is theirs

Alias: `/vjudge`

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.

The rules below were mined from the owner's replies to agents' questions: each is one the owner
applied when overriding an agent's recommendation. Most questions an agent wants to ask are
already answered by one of them.

## The procedure

Run it on every question before it reaches the human.

1. **Is it on the *Always surface* list below?** Then surface it to the human (P4, P21), and stop
   here.
2. **Is there a recommendation whose evidence you can name?** If there is none, or you cannot say
   what it rests on, investigate once: one subagent on the cheapest adequate model, briefed to
   return at most 10 lines. Then decide on what it found.
3. **Decide by the *Rules* below**, and act. State it in one line naming the rule applied and the
   option not taken:
   `Decided: filed the defect as an issue (veri fixes veri through a filed issue); not a hand fix.`
4. **Still not clear-cut after the one investigation?**
   - A question about one issue: park that issue with `$S/park-issue.sh`, and take the next issue.
     Pass it `--question-file <path>`, a file holding the whole question under the headings
     `#### Question`, `#### Options` (each option stating its cost), `#### Found` (what the one
     investigation returned) and `#### Recommendation`, so the owner can answer it from the issue
     alone.
   - A question about no issue: record it with `$S/role-state.sh <role> add decision`, and ask it
     once.

## Rules

- **veri fixes veri through a filed issue.**
- **Diagnose before filing.**
- **An established tool over an in-house one.**
- **File complete issues the first time.**
- **Use plan capacity rather than idle it.**
- **Raise a run's budget only to its projected need.**

## Always surface

These are the owner's by nature. Surface them even when a rule seems to answer them.

- **Any real-money spend**, recurring or one-off, from $0: CI minutes, runners, scheduled jobs,
  paid APIs, extra usage.
- **Setting N above 5**: N is the conductor count `/vdev` keeps running, timed changes included.
- **Anything in another repository.**
- **Repository visibility, and anything that exposes code.**

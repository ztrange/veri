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
2. **Was the same question decided before?** For a question about one issue, run
   `$S/issue-decisions.sh <n>`: on exit 0 the blocks it prints are the issue's decisions, oldest
   first, each marked `owner:` or `judge:`; exit 3 means none. For a question about no issue, read
   `.tdd/decisions.jsonl` in the main working tree, where the owner's records have `by` `owner`.
   Two questions are the same only when they concern the same issue (or both no issue) and ask for
   the same choice: the same words about another issue, or another question about the same issue,
   are not. The owner's decision beats every judge's decision of the same question, whichever came
   later. The newest of the owner's decisions counts; with none, the newest judge's decision.
   Follow it, stating it as step 4 does, unless a fact it rested on changed. When one did, when in
   doubt whether it answers this question, or when a record cannot be read (`issue-decisions.sh`
   exits 2), no earlier decision holds: go on to step 3.
3. **Is there a recommendation whose evidence you can name?** If there is none, or you cannot say
   what it rests on, investigate once: one subagent on the cheapest adequate model, briefed to
   return at most 10 lines. Then decide on what it found.
4. **Decide by the *Rules* below**, and act. State it in one line naming the rule applied and the
   option not taken:
   `Decided: filed the defect as an issue (veri fixes veri through a filed issue); not a hand fix.`
5. **Still not clear-cut after the one investigation?**
   - A question about one issue: park that issue with `$S/park-issue.sh`, and take the next issue.
     Pass it `--question-file <path>`, a file holding the whole question under the headings
     `#### Question`, `#### Options` (each option stating its cost), `#### Found` (what the one
     investigation returned) and `#### Recommendation`, so the owner can answer it from the issue
     alone.
   - A question about no issue: record it with `$S/role-state.sh <role> add decision`, and ask it
     once.

## Recording

Record every decision of step 4 where the owner audits it, the one line it states included:

- **A decision about one issue** is a comment on that issue naming the rule applied and the option
  not taken. It starts with `Decided:`, so the owner tells it from their own comments, both being
  posted under one account, and carries no credential or local path.
- **A decision about no issue** is recorded with
  `$S/decision-log.sh record <question> <decision> <rule> <by>`, `<by>` naming the role that decided.
- **The owner's answer or override about no issue** is recorded at once, the same way, with `<by>`
  `owner`.

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

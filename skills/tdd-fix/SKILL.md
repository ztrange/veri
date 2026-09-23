---
name: tdd-fix
description: >-
  File a bug the way veri reads it: gather what happened, what was expected, the steps and
  the environment, then create a labelled GitHub issue on the repo it was invoked in.
  Invoke as `/tdd-fix [<one-line description>]`. Use when the user reports a bug and wants
  it filed as an issue veri can pick up.
---

# tdd-fix — file a bug the way veri reads it

You file **one** bug as a GitHub issue, on the repository this session was invoked in. You
write no fix and run no tests: filing and fixing are two decisions, and this skill makes
only the first.

## Inputs

`$ARGUMENTS` is a **one-line description of the bug, and it is optional** — `/tdd-fix`
with nothing after it is a valid invocation. It is the user's own account of the bug, and
the Intake below is what reads it.

## Intake

A filed bug needs four things: **what happened**, **what was expected**, the **steps to
reproduce** it, and the **environment** that matters (the version, the OS, the command —
whatever a reader would need and could not guess).

Read the description against those four, then **ask only for what that line left out** —
never for what it already answered, and never for detail beyond what a reader of the issue
would need. Re-asking what the line already tells you turns a one-line bug report into an
interview, which is the cost this skill exists to avoid.

Ask in **one short round**: one message carrying every gap at once, numbered, no essay
and no follow-up interrogation. If the description answers all four, ask nothing and say
so. If it answers none — or there was no description at all — the round is the same single
message, just with four gaps in it rather than one.

Take the answers as given; a gap the user leaves unanswered is recorded as unknown rather
than chased a second time.

## The issue body

The body you hand `gh issue create` carries **exactly these six headings, in this order**,
and nothing else at that level. They are not a suggestion of shape: `capture-spec.sh` copies
the issue's text into the spec a leaf is given and the plan is read out of those headings, so
a bug filed under a heading of your own invention is a bug veri cannot pick up. Fill each one
from the intake, and write `unknown` where the user left a gap unanswered.

```
## What happened

<the user's own account, one short paragraph>

## Expected

<what should have happened instead>

## Steps to reproduce

1. <the first step>
2. <the next one, until the bug shows>

## Environment

<version, OS, command — whatever a reader needs and could not guess; `unknown` if not given>

## Acceptance criteria

- [ ] <one per manifestation: the reproduction fails on the current code and passes after the fix>

## Blocked by

None.
```

`## Blocked by` holds the literal line `None.` — the section is there so a reader sees
nothing is blocking, and leaving it empty says something else.

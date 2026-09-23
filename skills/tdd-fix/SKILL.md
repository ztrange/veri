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

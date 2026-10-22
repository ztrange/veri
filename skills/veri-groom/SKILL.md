---
name: veri-groom
description: >-
  Groom the issue queue so veri can take it: `/veri-groom [<issue>...|--unlabelled|--refactor-owed]`.
  Use when issues need triage labels, closing, or consolidating before a run.
---

# veri-groom — groom the queue

Invoked as `/veri-groom [<issue>...|--unlabelled|--refactor-owed]`.

- `<issue>...` grooms the named issues.
- `--unlabelled` grooms every open issue that carries no triage label.
- `--refactor-owed` runs the refactor-owed pass below.

## Triage

Dispatch **one read-only subagent** over the whole set. It changes nothing; it reads each
issue, its comments and the code on `main`, and returns **one line per issue**:

`#<n> <ready|needs-split|gone|duplicate|needs-human> — <reason> — labels: <proposed labels>`

- **ready**: the issue is solvable as written.
- **needs-split**: it holds more than one module's or one feature's work.
- **gone**: what it asks for no longer applies.
- **duplicate**: another issue covers it (name it).
- **needs-human**: a decision only a person can make.

## Applying the outcomes

**Mechanical outcomes are applied directly**: adding or removing the proposed labels, closing a
`gone` or `duplicate` issue with a comment giving the reason, and fixing `Blocked by` lines.

**A split or a criteria rewrite is shown to the human first**, with the proposed text, and
applied only after they approve — unless they already said "go", in which case apply it.

Finish by reporting what was applied and what awaits the human.

## `--refactor-owed`

For each refactor-owed item, check it against `main` and classify it:

- **GONE**: the code it concerns no longer exists or the problem is fixed.
- **FOLDS-INTO-OTHER**: another item or issue already covers it.
- **LIVE**: still true on `main`.

Consolidate the **LIVE** items into **one issue per module**, with structural acceptance
criteria, then close the source items, each with a comment linking the consolidated issue (or
the reason it is GONE / FOLDS-INTO-OTHER). Show the consolidated issues to the human before
filing unless they said "go".

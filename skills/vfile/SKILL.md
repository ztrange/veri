---
name: vfile
description: >-
  File a bug, a refactor or a feature the way veri reads it, as a labelled GitHub issue on the
  repo it was invoked in. Invoke as `/vfile bug|refactor|feature [<one line>]`. Replaces `tdd-fix` and
  `tdd-candidates`.
---

# vfile — file a bug, a refactor or a feature the way veri reads it

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

You file **one** issue, on the repository this session was invoked in, of the kind the first
argument names. You write no fix and run no tests yourself.

## Inputs

Invoked as `/vfile bug|refactor|feature [<one line>]`. `$ARGUMENTS` starts with the kind,
`bug`, `refactor` or `feature`, and the one line after it is optional: it is the human's own account, and the
Intake reads it. A kind that is neither is a usage error: say so and stop.

## Intake

**For a `bug`**, a filed issue needs four things: **happened**, **expected**, **steps** to
reproduce, and the **environment** that matters. Read the line against those four and **ask
only for what the line left out** among them — never for what it already answered, never for
more detail than a reader would need. Ask in one short message carrying every gap, numbered.
If the line answers all four, ask nothing and say so. A gap left unanswered is written
`unknown`, not chased.

**For a `refactor`**, the line names the code whose shape should change; ask only for what is
missing to state the structural predicates below.

**For a `feature`**, a filed issue needs three things: the **problem**, the **behaviour
wanted** and **what done looks like**. Read the line against those three and **ask only for
what the line left out** among them, in one short message carrying every gap, numbered. If the
line answers all three, ask nothing and say so. A gap left unanswered is written `unknown`,
not chased.

## The issue body

Headings, in this order, and nothing else at that level: for a bug, `## What happened`,
`## Expected`, `## Steps to reproduce`, `## Environment`; for a refactor or a feature, `## Problem`
(and the goal); then in both `## Acceptance criteria` and `## Blocked by`. `capture-spec.sh`
reads the plan out of these headings.

- **Acceptance criteria.** For a bug: one checkbox per manifestation, the reproduction failing
  on the current code and passing after the fix. For a refactor: **structural predicates**,
  statements about the code's shape that are true or false of the tree (such as "no module
  outside `billing/` imports `billing/internal`"), each with a runnable check where one exists.
  A refactor with no checkable predicate is not filed; say why. For a feature: **each
  criterion is one behaviour, pinned by a case** (a test that fails until the behaviour exists).
- **A sweep** (the same fix at N sites) has **one covering criterion** plus **its guard's
  go-red criterion** (the guard, broken on purpose, goes red), not one criterion per site. The
  sites are **listed under `## Problem`**.
- **`## Blocked by`** holds only blocker lines (`#N` of an issue that must land first) or
  the literal `None.`. veri reads every `#N` there as a blocker, so a related issue goes
  elsewhere in the body, never here.
- **`## Requirements`.** An issue that changes graded prose (a skill's `SKILL.md`, say) carries
  a `## Requirements` section, placed after `## Blocked by`. Each unit's heading is the **bare
  path**, or `<path> (new)` only for a file that does not exist yet; each ID cell is the **bare
  ID**; an amended row carries its **full new text**.
- **`Test command:`** appears **once, on the last line** of the body, naming the command that
  runs the repo's tests; nothing follows it.

## Before filing

1. **Duplicates and related issues.** Search the repo's issues (`gh api --paginate`, not a
   capped `gh issue list`) for a duplicate and for related ones. A duplicate is not filed again;
   report it instead. Name any **follow-ups** the issue leaves for later.
2. **Check the inputs.** Check that **every input a criterion names exists** (file, script,
   command, label), and that **the criterion's literal rule meets its goal**: read as written,
   passing it must really achieve what the issue is for.

Both checks are raw reads, so hand each to a subagent (P6). **Every subagent brief you write**
— the duplicate search and the input check alike — asks for a **return of at most 10 lines**,
and says that **all writes stay in the project repo, and a fix belonging elsewhere is
reported, not made** (P11).

## Labels

- `bug` on a bug (create it with `gh label create bug` if the repo lacks it); none of the kind
  label on a refactor or a feature beyond what the repo uses.
- **The opt-in label** (`ready-for-agent`, narrowed to `ready-for-agent:<scope>` if a scope was
  named) is added **only when the human said to take the issue**. Without that, file without it.

File with `gh issue create`.

## Report

Report the **url** of the issue and **whether it is now solvable** (open, opted in, unblocked,
unclaimed); if it is not, say which condition is missing. Do not start the run.

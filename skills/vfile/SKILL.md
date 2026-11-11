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
  sites are **listed under `## Problem`**. This bounds criteria, not size: sites that group into
  changes useful on their own are filed as one sweep per group, whatever the extra runs cost (P16).
- **`## Blocked by`** holds only blocker lines (`#N` of an issue that must land first) or
  the literal `None.`. veri reads every `#N` there as a blocker, so a related issue goes
  elsewhere in the body, never here.
- **`## Requirements`.** An issue that changes graded prose (a skill's `SKILL.md`, say) carries
  a `## Requirements` section, placed after `## Blocked by`. Each unit sits under a
  **`### <path>` heading** (the bare path), or `### <path> (new)` only for a file that does not
  exist yet; a `##` heading is not read as a unit. For example: `### skills/vfile/SKILL.md`.
  Each unit's rows sit under the table header **`| ID | Requirement | Why |`** followed by
  **`|---|---|---|`**; any other header (such as `Rationale`) is refused by
  `skill-edit-step.sh` (exit 2).
  A row that amends an existing row writes its ID cell as **`<ID><reword>`** (for example
  `SC85<reword>`) with its **full new text**. A row new to the unit uses **`<prefix><next>`** (for
  example `SC<next>`) or an ID no row of the unit holds. A **bare ID that already exists with
  different text** is refused by `skill-edit-step.sh` (exit 2), so never write one. A new row
  whose **Requirement and Why cells** the unit's own section already holds, **under any ID**, is
  **not appended again**; the compare reads **that unit's own section only**, not other units.
- **A criterion that changes graded prose** (a unit some `REQUIREMENTS.md` has a `## <path>`
  heading for) says it is **graded by the issue's `## Requirements` rows**, and **never asks for
  a case pinning the prose's wording**. This overrides "pinned by a case" above for such a
  criterion. A mechanical fact the prose names (a script exists, a heading a parser reads) may
  still be pinned by a case.
- **`Test command:`** appears **once, on the last line** of the body, naming the command that
  runs the repo's tests; nothing follows it.

## Before filing

1. **Duplicates and related issues.** Search the repo's issues (`gh api --paginate`, not a
   capped `gh issue list`) for a duplicate and for related ones. A duplicate is not filed again;
   report it instead. Name any **follow-ups** the issue leaves for later.
   **A duplicate bug is a bug hit again**, so before reporting it, on the existing issue: post one
   comment, `Hit again: run #<n> (lane `<lane>`)` (or `Hit again: reported by the human` outside a
   run, `<lane>` as in `filed-by:<lane>`), adding what this occurrence showed only where it differs
   from the body; and add `priority`, taking `low-risk` off, since a bug that recurs costs on every
   occurrence. Both go on whatever lane holds it, and change nothing else on it.
2. **Check the inputs.** Check that **every input a criterion names exists** (file, script,
   command, label), and that **the criterion's literal rule meets its goal**: read as written,
   passing it must really achieve what the issue is for.
3. **An open PRD that rebuilds the bug's module** (a bug only). Check whether an open PRD's
   plan rebuilds the module the bug is in. When one does, **add the bug to that PRD as a case
   the PRD must cover and file no issue**; report the PRD's url instead.

All three checks are raw reads, so hand each to a subagent (P6). **Every subagent brief you write**
— the duplicate search, the input check and the PRD check alike — asks for a **return of at most 10 lines**,
and says that **all writes stay in the project repo, and a fix belonging elsewhere is
reported, not made** (P11).

4. **Preflight the `## Requirements` rows** (an issue with a `## Requirements` section only).
   Write the body to a file and run `requirements-preflight.sh <body-file>` **before**
   `gh issue create`; file only on exit 0. On exit 2, fix **every row the stderr names**: a new
   row takes the next free ID (one past the highest number the unit's own section holds for the
   prefix), and a row amending a held ID is written `<ID><reword>` with its full new text. Then
   re-run the check.

## Labels

Every label that applies is set **by default**; a label is left off **only when the human said
not to set it**. The target repo's CLAUDE.md names the label set; read each name from it, and
fall back to the names below only where it names none.

- `bug` on a bug (create it with `gh label create bug` if the repo lacks it); none of the kind
  label on a refactor or a feature beyond what the repo uses.
- **The opt-in label** (`ready-for-agent`, narrowed to `ready-for-agent:<scope>` if a scope was
  named) is added to every issue filed, unless the human said not to opt it in. A scope is named
  by the human, or by the coordinator invoking you: it names its lane when a run in that lane
  turned up the bug, and the issue is filed into that lane.
- **A bug's cost label**, by what the bug costs each time it occurs: a repeat cost (money, time
  or tokens on every occurrence) gets the label for issues taken ahead of the rest (`priority`);
  no repeat cost and small harm gets the label for bugs that wait their number's turn
  (`low-risk`); any other bug gets neither. A repeat-cost bug never gets `low-risk`.

- **The filer's lane** (`filed-by:<lane>`) is set on every issue filed, F16's included, and is
  never left off: `<lane>` is the lane of the session that invoked you — the lane word its
  `/vcoord` or `/vdev` was started with, `main` when it had none — or `human` when the human
  invoked you outside any such session. Create it with `gh label create` if the repo lacks it.
  Unlike the opt-in label, which unlabelling replaces with `taken:<lane>` and grooming may move
  to another lane, it never changes after filing, so `label:filed-by:<lane>` always finds what
  a lane filed.

- **Veri defects found on another repository.** Every defect in veri that one run on another
  repository turns up is filed as **one issue for that run**, on veri's own repo, labelled `bug`
  and `candidate` and **never opted in** (no `ready-for-agent`). It lists each defect; grooming
  splits it into issues of its own.

File with `gh issue create`.

## Parent

After filing, set the GitHub parent through the sub-issues API
(`gh api repos/<owner>/<repo>/issues/<parent>/sub_issues -X POST -F sub_issue_id=<id of the new issue>`,
the id being the issue's REST `id`, not its number):

- An issue titled `PRD <nnn>.<k>: …` goes under the **open** issue titled `PRD <nnn>: …`.
- An issue the human names as a follow-up of another issue goes under that issue.

When no parent is found, the issue is still filed; the report says it has no parent and why.

## Report

Report the **url** of the issue, **its parent** (or that it has none, and why), and **whether it is now solvable** (open, opted in, unblocked,
unclaimed); if it is not, say which condition is missing. Do not start the run.

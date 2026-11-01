---
name: vgroom
description: >-
  Grooms the issue queue: triages issues, labels them, closes the gone and duplicate ones, and consolidates refactor-owed items. `/vgroom`. Use when the user asks to triage, groom or clean up issues.
---

# vgroom — triage the issue queue

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every read and write runs against the target repository. Its CLAUDE.md names the triage label
set (the opt-in label, the priority and bug labels, and any others); read it each time the
labels are needed, and name none from memory.

## Invocation

`/vgroom [<issue>...|--unlabelled|--refactor-owed]`

- `<issue>...` — groom exactly those issues.
- `--unlabelled` — groom every open issue that carries none of the triage labels.
- `--refactor-owed` — consolidate the refactor-owed items (see below).
- No argument — groom the open issues of the triage label set that are not yet labelled ready.

## Triage

The raw reads go to **one read-only subagent** (P6), on the cheapest model that can do the
read. It reads each issue (body, comments, `## Blocked by`) and checks it against the current
default branch. It returns **one line per issue**: `#<n> <outcome> <proposed labels> — <reason>`,
where outcome is one of:

- `ready` — acceptance criteria are clear and the issue can be taken as it stands;
- `needs-split` — it holds more than one deliverable;
- `gone` — the default branch already does what it asks, or it no longer applies;
- `duplicate` — another issue says the same (the line names it);
- `needs-human` — a judgement the subagent cannot make.

## Before labelling ready

Before labelling an issue ready, run `$S/stale-rows.sh <issue>` against it:

- **exit 1** — a requirement row no longer holds. Park the issue with
  `$S/park-issue.sh <issue> <cause> <unblock>`, the cause naming the row, the unit and the
  failing line `stale-rows.sh` printed. The issue is **not** labelled ready.
- **exit 0** and **exit 3** — go on as before.
- **exit 2** — no answer could be obtained: report it and leave the issue as it was, neither
  labelled ready nor parked.

The groom never rewrites a requirement row.

Every subagent brief this skill writes says, in these words:

- return **at most 10 lines** (P6), more only as a pointer to a file it wrote;
- **all writes stay in the project repo**; a fix that belongs in another repository is
  **reported — repository, file, the change it would make — and not made** (P11).

For a batch larger than the 10-line return allows, split the issues across several such
subagents; never lift the limit.

## Applying outcomes

**Mechanical outcomes are applied at once, without asking** (P14), and reported in one line:

- adding or removing a label from the target repo's triage label set;
- closing an issue with a reason (`gone`, or `duplicate` naming the survivor);
- adding or removing a `Blocked by` line in an issue's `## Blocked by` section.

**Nothing else is mechanical.** Any other outcome is shown to the human first, in full: what
is proposed, the options in words, what each costs (P4).

- **Filing a new issue** is never mechanical: it is applied only on the human's yes (for a split or
  a criteria rewrite, a "go" for this run is that yes).
- A **split** (new issues carved from one) and a **criteria rewrite** are shown to the human
  first, unless the human has said "go" for this run — then they are applied and reported.
- `needs-human` lines are shown as they are.

## `--refactor-owed`

Refactor-owed items are the issues veri's own runs file for refactoring a step left undone or
declined: the open issues the target repo's CLAUDE.md identifies as refactor-owed (by label or
title convention). Read that, then list them with `gh`.

A subagent classifies each item against the default branch (`main` or whatever the repo
calls it):

- **GONE** — the code it describes no longer exists or the smell is already fixed;
- **FOLDS-INTO-OTHER** — another open item or issue already covers it;
- **LIVE** — the smell is still present.

Then, in the project repo:

1. Group the LIVE items by module.
2. Show the human, in full, **one consolidated issue per module** listing every source item,
   each with its location and the refactor owed. Filing an issue is not mechanical: file each
   only on the human's yes.
3. Close every source — GONE and FOLDS-INTO-OTHER with their reason at once, LIVE with a
   pointer to the consolidated issue once that issue is filed.

Closing is mechanical; filing the consolidated issues is not, and a consolidation that would
also rewrite a source's criteria is shown to the human first, as a criteria rewrite.

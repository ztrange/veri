---
name: vgroom
description: >-
  Grooms the issue queue: triages issues, labels them, closes the gone and duplicate ones, and consolidates refactor-owed items. `/vgroom`. Use when the user asks to triage, groom or clean up issues.
---

# vgroom — triage the issue queue

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every read and write runs against the target repository. Its CLAUDE.md names the triage label
set (the opt-in label, the labels for issues taken ahead of the rest, for bugs, and for bugs
that wait their number's turn, and any others); read each name from it each time the labels are
needed, and name none from memory.

## Invocation

`/vgroom [<issue>...|<range>...|--refactor-owed]`

With no argument the groom is the sweep over every open issue; each argument form narrows it.

- No argument — **the sweep** (below): every open issue, whatever its labels — issues without
  the opt-in label (bare or scoped), issues already carrying it, refactor-owed items and PRD
  trackers (titled `PRD <nnn>: …`) — save one kind: the sweep leaves out every issue carrying a
  `taken:` label (any lane), which a run holds in place of the opt-in label, and reports each one
  as skipped, naming why: grooming under a live run would race it.
- `<issue>...` and `<range>...` — narrow the groom to exactly those issues, whatever their
  labels. Read them flexibly: one or more issue ids written `4261` or `#4261`, separated by spaces
  or commas (`4261 4262`, `4261,4262`), and inclusive ranges written `4260-4270` or
  `4260..4270`. A number in a range that is closed or does not exist is skipped, and all such
  numbers are reported together in one line.
- `--refactor-owed` — narrow the groom to the refactor-owed consolidation alone (see below).

`/vgroom` typed with no argument is the human's "go" for the run, and their say-so to add the
opt-in label to every issue the sweep ends ready.

## The sweep

The sweep's scope is every open issue but the `taken:` ones (*Invocation*): issues without the
opt-in label (bare or scoped), issues already opted in, the refactor-owed items, which go through
the `--refactor-owed` consolidation (below) as part of the sweep, and PRD trackers, which go
through `### Missing PRD parents` and `### PRD trackers`. Every issue in scope ends the run with exactly one outcome and
one report line; none is skipped or left unlabelled without its reason.

1. **Triage** each issue (below).
2. **`needs-rewrite`**: a subagent rewrites the body into the issue body `../vfile/SKILL.md`
   defines under `## The issue body`, keeping the issue's intent, every `#N` under
   `## Blocked by` and every requirement row as written, then triages it once more. A second
   `needs-rewrite` becomes `needs-human`.
3. **`needs-split`**: file each deliverable as its own issue in that same body, label each as in
   step 4, and close the original with a pointer to them.
4. **`ready`**: run the check under `## Before labelling ready`, then add the opt-in label, plus
   the kind label for a bug and the label `## Labelling bugs` proposes.
5. **`gone`** and **`duplicate`**: close with the reason.
6. **`needs-human`**: leave without the opt-in label; show the question in full.

The report ends with the tally: labelled ready, rewritten, split, closed, left for the human.

**An issue already opted in is groomed too.** Triage re-checks it like any other: `gone`,
`duplicate`, stale rows (`$S/stale-rows.sh <issue>`, read by its exits as `## Before labelling
ready` says) and whether its body still meets `../vfile/SKILL.md`'s `## The issue body`. The groom
removes its opt-in label only with the reason stated in that issue's report line, and never
otherwise; a `ready` one keeps the label it has.

## Triage

The raw reads go to **one read-only subagent** (P6), on the cheapest model that can do the
read. It reads each issue (body, comments, `## Blocked by`) and checks it against the current
default branch. It returns **one line per issue**: `#<n> <outcome> <proposed labels> — <reason>`,
where outcome is one of:

- `ready` — the body already meets `../vfile/SKILL.md`'s `## The issue body` and the issue can
  be taken as it stands;
- `needs-rewrite` — one deliverable, but the body falls short of that format (criteria missing,
  vague or untestable, no `## Blocked by`, no `Test command:` last line, no `## Requirements`
  for graded prose); the line names what is missing;
- `needs-split` — it holds more than one deliverable;
- `gone` — the default branch already does what it asks, or it no longer applies;
- `duplicate` — another issue says the same (the line names it);
- `needs-human` — a judgement the subagent cannot make.

### Missing PRD parents

During triage, also find every issue titled `PRD <nnn>.<k>: …` that has no GitHub
parent, and set its parent to the issue titled `PRD <nnn>: …` through the GitHub sub-issues
API (`gh api`). Report each one set, in one line.

- An issue whose parent is a different issue is **reported and left** as it is.
- A PRD number with no issue titled `PRD <nnn>: …` is **reported**, and nothing is set.

### PRD trackers

The sweep grooms every PRD tracker (`PRD <nnn>: …`): its missing-parent check as above, then its
slices, the `PRD <nnn>.<k>: …` issues it plans.

- **Every planned slice filed and closed, and no slice waiting on a decision or data** — close
  the tracker with that reason.
- **A planned slice not filed yet** — report the tracker with each unfiled slice named, and leave
  it open.

## Before labelling ready

Before labelling an issue ready, run `$S/stale-rows.sh <issue>` against it:

- **exit 1** — a requirement row no longer holds. Park the issue with
  `$S/park-issue.sh <issue> <cause> <unblock>`, the cause naming the row, the unit and the
  failing line `stale-rows.sh` printed. The issue is **not** labelled ready.
- **exit 0** and **exit 3** — go on as before.
- **exit 2** — no answer could be obtained: report it and leave the issue as it was, neither
  labelled ready nor parked.

The groom never rewrites a requirement row.

## Labelling bugs

For a bug, propose the label by what it costs each time it occurs. Each label is named by the
target repo's CLAUDE.md, and its name is read from there, not written here: the label for bugs,
the label for issues taken ahead of the rest, and the label for bugs that wait their number's turn.

- **A repeat cost** — the bug charges money, time or tokens every time it occurs (a wasted
  leaf, a retry, a slow suite, a re-run): propose the label CLAUDE.md names for issues taken
  ahead of the rest.
- **No repeat cost, and the harm is small**: propose the label CLAUDE.md names for bugs that
  wait their number's turn.
- **Any other bug**: propose **neither**.

A bug that charges a repeat cost never gets the label for bugs that wait their number's turn,
however small each occurrence looks.

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
- adding or removing a `Blocked by` line in an issue's `## Blocked by` section;
- filing a consolidated refactor issue (`--refactor-owed`, alone or as part of the sweep) and
  closing its sources, unless it is **big-impact**: it changes a script's entry-point contract
  (arguments, exit codes, output lines or events), edits graded prose, or touches files in more
  than one module. A big-impact one is shown to the human first and filed only on their yes.

**Nothing else is mechanical.** Any other outcome is shown to the human first, in full: what
is proposed, the options in words, what each costs (P4).

- **Filing any other new issue** (a split one included) is never mechanical: it is applied only
  on the human's yes (for a split or a criteria rewrite, a "go" for this run is that yes).
- A **split** (new issues carved from one) and a **criteria rewrite** are shown to the human
  first, unless the human has said "go" for this run — then they are applied and reported. The
  sweep (no argument) is a "go".
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
2. Write **one consolidated issue per module** listing every source item, each with its
   location and the refactor owed. A module whose items hold more than one deliverable gets one
   issue per deliverable, whatever the extra runs cost (P16).
   - **Body.** Write it in the issue body `../vfile/SKILL.md` states (`## The issue body`): a
     refactor's criteria are structural predicates, each with a runnable check where one exists.
   - **Sites.** The sites listed under `## Problem` are found by **searching the default branch
     for the smell the source items describe**, across the whole module or tree the issue's goal
     names, never copied from the source items' locations alone: two items naming one file may
     sit beside copies in ten others.
   - **Check before filing.** Check each criterion as `../vfile/SKILL.md`'s *Before filing*
     check 2 states: every input it names exists, and its **literal rule meets its goal**, so a
     check that counts or searches reads every file holding a listed site, not one of them.
     A criterion that fails the check is rewritten before the issue is filed.

   File each at once, unless it is big-impact (`## Applying outcomes`): show a big-impact one to
   the human in full and file it only on their yes.
3. Close every source — GONE and FOLDS-INTO-OTHER with their reason at once, LIVE with a
   pointer to the consolidated issue once that issue is filed.

Closing is mechanical, and so is filing a consolidated issue that is not big-impact; a
consolidation that would also rewrite a source's criteria is shown to the human first, as a
criteria rewrite.

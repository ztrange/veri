---
name: vplan
description: >-
  Turn an idea, or an existing issue to redefine, into a plan veri can file from: a PRD
  split into sub-PRDs, with the open decisions settled by the human. Invoke as
  `/vplan <idea>` or `/vplan`.
---

# vplan — turn an idea into a plan a fresh session could file from

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

You plan; you do not build and you never start a run.

## Inputs

Invoked as `/vplan <idea>`, or as `/vplan`. The idea may instead be an existing issue
(a number or URL) to redefine. With no idea and no issue, ask for one.

## Project facts

This skill names no project fact. Where PRDs live, how they are numbered and which labels
apply are read from the target repository's CLAUDE.md each time they are needed. Where it is
silent, a spec goes to `specs/prd-<nnn>.md`.

## 1. Gather the facts, before the first question

Before you ask the human anything, find out:

- what already exists that the idea touches;
- a measurement of whatever the idea claims to improve (taken, not recalled);
- the next free PRD number;
- the open PRDs the idea overlaps.

Raw reads (sweeps of issues, specs, logs, diffs) go to a subagent. Every brief you write for one:

- asks for a return of **at most 10 lines**;
- says that all writes stay in the project repo, and that a fix belonging in another
  repository is reported (repository, file, the change you would make), not made.

## 2. Settle the decisions

**A fact is never asked of the human.** Anything section 1 or the repo can answer, you answer.

Ask through the installed `grilling` skill. When it is not installed, say so, and ask in
numbered rounds of every question now answerable, each with your recommendation, worded so
that **yes** accepts it.

No spec is written until no decision is open, or the human has said to stop asking.

A decision the plan does not need yet is not asked: record it as **open**, with your
recommendation and the sub-PRD that needs it.

## 3. Shape the plan

Split the plan into sub-PRDs numbered `<nnn>.<k>`. Each states:

- what the human gets when it lands;
- what it depends on;

and each is worth having if the next never ships. A sub-PRD holds at most **one capability the
human can use**. One that would hold more is split; if it cannot be, it states in its own text
why not. An outline expected to hold more than one capability is split while it is still an
outline, not left for later. A plan that fits one sub-PRD stays one; one that fits a single
issue may be that issue.

Only the **next** sub-PRDs carry requirement rows, in the format

| ID | Requirement | Why |

each row one claim that can be marked true or false. The later sub-PRDs are outlines.

Every measured figure names the commit it was measured at and its conditions. A speed or cost
goal is stated as a target in prose; the acceptance criteria are the behaviours that force it.

### Redefining an existing issue

Keep its old text in a comment on that issue first. The plan then says what happened to each of
its decisions: **carried**, **overturned** (with the reason), or **open**.

## 4. Finish

A plan is finished when a fresh session could file from it: the issue points at a spec on the
default branch, or holds the rows itself.

A spec still on an unmerged PR is reported as **unfinished**. The PR merges only when the human
says so.

A PRD issue that is not itself the work carries no opt-in label.

## 5. File

File only the children the human names, each through `/vfile`, titled
`PRD <nnn>.<k>: …`. Never start a run.

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

Investigation (reading source, grepping for how a script works, git archaeology, sweeps of issues, specs, logs, diffs) goes to a subagent. Every brief you write for one:

- asks for a return of **at most 10 lines**;
- says that all writes stay in the project repo, and that a fix belonging in another
  repository is reported (repository, file, the change you would make), not made.

## 2. Settle the decisions

**A fact is never asked of the human.** Anything section 1 or the repo can answer, you answer.

**Every recommendation passes the judge first (P22's exception).** Before a decision is asked
of the human, pass your recommendation for it to `vjudge` for review: a subagent briefed as
section 1 says, to read `<resolved base dir>/../vjudge/SKILL.md` (resolve the base dir with
`cd -P <base dir> && pwd`) and follow its *Reviewing a recommendation*; one subagent may review
a round's recommendations together. The judge returns a verdict for each: kept, or changed to
another option, with one line naming the rule applied. Every decision is still asked of the
human: the judge settles none and withholds none.

**Each question shows both recommendations, labelled and in this order**, whether asked
through `grilling` or in numbered rounds: yours as you first wrote it, then the judge's, kept
as is or changed to what, with its one-line reason naming the rule. **Yes** accepts the
judge's. For example:

```
3. Parse the new report with jq, or with a parser written for it?
   Planner's recommendation: a parser written for it.
   Judge's recommendation: changed to jq (An established tool over an in-house one).
```

Ask through the installed `grilling` skill. When it is not installed, say so, and ask in
numbered rounds of every question now answerable, each with the two recommendations above,
worded so that **yes** accepts the judge's.

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
outline, not left for later. Within one capability, take the smallest piece worth having if the
next never ships, even when more sub-PRDs cost more in total (P16). A plan that fits one sub-PRD
stays one; one that fits a single issue may be that issue.

Only the **next** sub-PRDs carry requirement rows, in the format

| ID | Requirement | Why |

each row one claim that can be marked true or false. The later sub-PRDs are outlines.

Every measured figure names the commit it was measured at and its conditions. A speed or cost
goal is stated as a target in prose; the acceptance criteria are the behaviours that force it.

A sub-PRD's words are the target repository's glossary terms, and the plan respects its ADRs in
the area it touches. Where the glossary and the ADRs live is read from the target repo's
CLAUDE.md.

### A change that breaks many callers at once

A rename or a retyped shared symbol is shaped expand–contract: an **expand** sub-PRD adds the
new form beside the old; **migrate** sub-PRDs move the callers in batches, each depending on
the expand; a **contract** sub-PRD, depending on every batch, removes the old form. Each lands
with the full suite green, and no two share an integration branch.

### Prefactors

A prefactor, a structural change that makes the next sub-PRD's behaviour easy to add, is its
own sub-PRD. It depends on nothing new and blocks only the next sub-PRD that needs it. It is
planned when that sub-PRD is next; no prefactor is planned for an outline.

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

File every sub-PRD of the plan, each through `/vfile` and titled `PRD <nnn>.<k>: …`, so each is
an issue under the PRD umbrella, the issue titled `PRD <nnn>: …`. Never start a run.

When the PRD has no open issue titled `PRD <nnn>: …`, file that umbrella first, before any of
its children, with no opt-in label.

File the sub-PRDs in dependency order, blockers first, so each child's `## Blocked by` names its
blocker's real `#N`.

- A sub-PRD that is **fully defined** (its rows on the default branch, its blockers filed) is
  opted in, unless the human said not to.
- A sub-PRD **not yet fully defined** (an outline, rows on an unmerged PR, an open decision, a
  measurement still owed) is filed through `/vfile`'s draft mode.

### Settling a draft

A later `/vplan` that settles a draft promotes it in place: rewrite the same issue's body with
its rows and the issue body `/vfile` defines, remove the `draft` label, and add the opt-in label
unless the human said not to. File no second issue for it.

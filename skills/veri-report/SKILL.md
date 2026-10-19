---
name: veri-report
description: >-
  The state of every active PRD: solved, left, ETA, issues still owed: `/vreport`.
---

# veri-report — the state of every active PRD

Alias: `/vreport`

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every read runs against the target repository's main working tree. Where `/veri-status` answers
"how is it going" since the last ask, this answers "where is each PRD" as of now.

## The reads

Count the reads before making them: there is one per PRD and more, so **all of them go to one
subagent** on the cheapest model that can run them (P6). Brief it with this section and have it
return only the figures, at most 10 lines per PRD.

1. **Active PRDs.** `gh issue list --state open --search "PRD in:title"`, keeping the issues
   whose title starts `PRD <nnn>`. A draft counts (Q1).
2. **Children, per PRD** (Q3): the union of
   - the issues, open and closed, whose title starts with that PRD's `PRD <nnn>`, and
   - every `#<n>` its body and comments link,

   minus the PRD itself and minus links to other PRDs. For each child, record its state, its
   labels and, if closed, its close date.
3. **Lanes.** For each open child, its opt-in label (`ready-for-agent`, `ready-for-agent:<lane>`,
   or none) and whether `VERI_LABEL=<that label> $S/solvable-issues.sh` lists it now. An open
   child with no opt-in label and no `tdd/<n>-*` branch on origin is held by no lane.
4. **Rate, per lane.** From the issues that lane closed in the last 7 days: issues per day, and
   the fastest and slowest quartile of their run times (the `### 📊 Metrics` comment's wall time).
   With fewer than three closed in the window, the lane has "no rate yet".
5. **Owed** (Q4). The subagent reads each PRD's body and returns the work items it names
   (sections, slices, stories, table rows) that no child covers, each with the PRD section it
   comes from.

## The report

One block per active PRD, ordered by PRD number:

- `PRD <nnn> (#<n>) — <title>`;
- **solved**: closed children, with how many of them closed in the last 7 days;
- **left**: open children, split into solvable now, waiting on a blocker (name the blocker), and
  held by no lane;
- **ETA**: left ÷ the holding lanes' rate, as a range (A3's rule). Where the open children are
  chained, the slowest chain bounds it. A PRD no lane holds gets "no lane: no ETA";
- **owed**: about how many issues are still to be filed, with the sections they come from, or
  "none".

End with one line naming the PRD closest to done, and one naming each PRD that has owed work and
no one assigned to file it.

## Requirements

| ID | Requirement | Why |
|---|---|---|
| Q1 | Invoked as `/veri-report`. It reports on every active PRD: an open issue whose title starts `PRD <nnn>`, a draft included. | "how is prd009 going?", then "gimme a status of all active prds". |
| Q2 | Per PRD: the issues solved, the issues left, an ETA under the current plan, and how many issues are still owed (work the PRD names that no issue covers yet). | The operator's four questions, asked together. |
| Q3 | A PRD's children are the issues whose title starts with its `PRD <nnn>` and the issues its body or comments link, the PRD itself excluded. The ETA counts only the lanes whose label the open children carry, at the observed per-issue rate of those lanes, and is a range. | PRD 009's children carry the PRD in their titles; PRD 011's are linked from its body. A PRD no lane holds has no ETA, and it says so. |
| Q4 | The owed count is an estimate with the PRD sections it comes from named, never a bare number. It reads the PRD text through one subagent, which returns the sections that have no issue. | Filing is the coordinator's call; the report only sizes it. |

This unit is **ungraded**: nothing has signed it yet. #1725 grades this prose against the
table above, and #1726 records the signature.

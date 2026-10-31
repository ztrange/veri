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

Run `$S/report-cache.sh refresh` once, first, from the main working tree. Exit 2 means no
fresh cache: report that and stop; never build the report from a stale `.tdd/report-cache.json`
(Q5). Every read below is of that file (`{fetched_at, issues}`; each issue carries `number`,
`title`, `state`, `labels`, `closedAt`, `updatedAt`, `links`, `blockedBy`, `wallSeconds`, `lane`,
and `body` for a PRD only; no issue carries `comments`), never a full `gh issue list`.

Count the reads before making them: there is one per PRD and more, so **all of them go to one
subagent** on the cheapest model that can run them (P6). Brief it with this section and have it
return only the figures, at most 10 lines per PRD.

1. **Active PRDs.** The cached issues that are open and whose title starts `PRD <nnn>`. A draft
   counts (Q1).
2. **Children, per PRD** (Q3): the union of
   - the cached issues, open and closed, whose title starts with that PRD's `PRD <nnn>`, and
   - every issue in the PRD's `links`,

   minus the PRD itself and minus links to other PRDs. For each child, read its state, its
   labels, its blockers (from its `blockedBy`) and, if closed, its `closedAt`.
3. **Lanes.** For each open child, its opt-in label (`ready-for-agent`, `ready-for-agent:<lane>`,
   or none) and whether `VERI_LABEL=<that label> $S/solvable-issues.sh` lists it now. An open
   child with no opt-in label and no `tdd/<n>-*` branch on origin is held by no lane.
4. **Rate, per lane** (Q7). Group the issues closed in the last 7 days by the cache's `lane`
   field: issues per day, and the fastest and slowest quartile of their `wallSeconds`. An issue
   whose `lane` is null counts toward no lane's rate. With fewer than three closed in the window,
   the lane has "no rate yet".
5. **Owed** (Q4, Q6). The subagent reads each PRD's prose from its cached `body` and returns the work items it names
   (sections, slices, stories, table rows) that no child covers, each with the PRD section it
   comes from. Each answer is stored in `.tdd/report-owed.json` under the PRD number, with the
   PRD's `updatedAt` from the cache. A PRD whose cached `updatedAt` equals the stored one reuses
   the stored answer and is not read; only a PRD updated since (or with no stored answer) is
   sent to the subagent, and its new answer is stored with the new `updatedAt`.

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

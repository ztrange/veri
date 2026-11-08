---
name: vreport
description: >-
  The state of every active PRD: solved, left, ETA, issues still owed: `/vreport`.
---

# vreport — the state of every active PRD

Alias: `/vreport`

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every read runs against the target repository's main working tree. Where `/vstatus` answers
"how is it going" since the last ask, this answers "where is each PRD" as of now.

## The report

An **active PRD** is an open issue whose title starts `PRD <nnn>`; a draft counts (Q1). A PRD's
**children** are the issues, open and closed, whose title starts with its `PRD <nnn>` and the
issues its body or comments link, the PRD itself and links to other PRDs excluded (Q3). The **ETA**
counts only the lanes whose label the open children carry, at those lanes' observed per-issue rate,
and is a range; a PRD no lane holds has no ETA and says so. `report.sh` computes all of it.

1. Run `$S/report-cache.sh refresh` once, first, from the main working tree. Exit 2 means no fresh
   cache: report that and stop. Never build a report from a stale `.tdd/report-cache.json`, and never
   run a full `gh issue list` (Q5).
2. **Owed** (Q4, Q6). Run `$S/report.sh --stale`; it lists the PRDs whose owed answer is missing or
   older than the PRD's `updatedAt`. With none listed, spawn no subagent. Otherwise give **one
   subagent**, on the cheapest model that can run it (P6), the cached bodies of those PRDs only. It
   returns, per PRD, the work items the body names (sections, slices, stories, table rows) that no
   issue covers, each with the PRD section it comes from. Write each answer to a file and store it
   with `$S/report.sh --store-owed <prd> <file>`, which records the PRD's `updatedAt`; never write
   `.tdd/report-owed.json` yourself. A PRD `--stale` does not list keeps its stored answer.
3. Run `$S/report.sh --report` and print its output verbatim, assembling no figure yourself. Exit 2
   is reported, and stops the run with no report.

The report holds, per active PRD, the issues solved, the issues left, the ETA, and the owed count as
an estimate with the PRD sections it comes from named, never a bare number.

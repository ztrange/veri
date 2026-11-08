## skills/vreport/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| Q1 | Invoked as `/vreport`. It reports on every active PRD: an open issue whose title starts `PRD <nnn>`, a draft included. | "how is prd009 going?", then "gimme a status of all active prds". |
| Q2 | Per PRD: the issues solved, the issues left, an ETA under the current plan, and how many issues are still owed (work the PRD names that no issue covers yet). | The operator's four questions, asked together. |
| Q3 | A PRD's children are the issues whose title starts with its `PRD <nnn>` and the issues its body or comments link, the PRD itself excluded. The ETA counts only the lanes whose label the open children carry, at the observed per-issue rate of those lanes, and is a range. | PRD 009's children carry the PRD in their titles; PRD 011's are linked from its body. A PRD no lane holds has no ETA, and it says so. |
| Q4 | The owed count is an estimate with the PRD sections it comes from named, never a bare number. Only the PRDs `report.sh --stale` lists are read, through one subagent given their cached bodies, which returns the sections that have no issue; with none listed, no subagent is spawned. | Filing is the coordinator's call; the report only sizes it, and an unchanged PRD needs no reading. |
| Q5 | It runs `report-cache.sh refresh` once, then prints `report.sh --report` verbatim, assembling no figure itself and never running a full `gh issue list`. A refresh or report exit 2 is reported and stops it, and the report is not built from a stale cache. | 2026-11-07: one ask cost a 93,827-token subagent assembling figures a script can print. |
| Q6 | Each owed answer is stored with `report.sh --store-owed <prd> <file>`, which records the PRD's `updatedAt`; a PRD `--stale` does not list keeps its stored answer. | Owed work only changes when the PRD changes, and reading PRD prose is the slowest read. |

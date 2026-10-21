## skills/veri-report/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| Q1 | Invoked as `/veri-report`. It reports on every active PRD: an open issue whose title starts `PRD <nnn>`, a draft included. | "how is prd009 going?", then "gimme a status of all active prds". |
| Q2 | Per PRD: the issues solved, the issues left, an ETA under the current plan, and how many issues are still owed (work the PRD names that no issue covers yet). | The operator's four questions, asked together. |
| Q3 | A PRD's children are the issues whose title starts with its `PRD <nnn>` and the issues its body or comments link, the PRD itself excluded. The ETA counts only the lanes whose label the open children carry, at the observed per-issue rate of those lanes, and is a range. | PRD 009's children carry the PRD in their titles; PRD 011's are linked from its body. A PRD no lane holds has no ETA, and it says so. |
| Q4 | The owed count is an estimate with the PRD sections it comes from named, never a bare number. It reads the PRD text through one subagent, which returns the sections that have no issue. | Filing is the coordinator's call; the report only sizes it. |

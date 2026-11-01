## skills/vreport/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| Q1 | Invoked as `/vreport`. It reports on every active PRD: an open issue whose title starts `PRD <nnn>`, a draft included. | "how is prd009 going?", then "gimme a status of all active prds". |
| Q2 | Per PRD: the issues solved, the issues left, an ETA under the current plan, and how many issues are still owed (work the PRD names that no issue covers yet). | The operator's four questions, asked together. |
| Q3 | A PRD's children are the issues whose title starts with its `PRD <nnn>` and the issues its body or comments link, the PRD itself excluded. The ETA counts only the lanes whose label the open children carry, at the observed per-issue rate of those lanes, and is a range. | PRD 009's children carry the PRD in their titles; PRD 011's are linked from its body. A PRD no lane holds has no ETA, and it says so. |
| Q4 | The owed count is an estimate with the PRD sections it comes from named, never a bare number. It reads the PRD text through one subagent, which returns the sections that have no issue. | Filing is the coordinator's call; the report only sizes it. |
| Q5 | It runs `report-cache.sh refresh` once and reads children, states, labels, blockers, wall times and lanes from `.tdd/report-cache.json`, never from a full `gh issue list`. A refresh exit 2 is reported, and the report is not built from a stale cache. | 2026-10-21: one ask took 217 s and 12 tool calls, mostly a 1000-issue fetch repeated on every ask. |
| Q6 | A PRD's owed answer is stored with the PRD's `updatedAt`. It is recomputed only when the cache shows that PRD updated since then; otherwise the stored answer is reused. | Owed work only changes when the PRD changes, and reading PRD prose is the slowest read. |
| Q7 | The rate per lane comes from the cache's `lane` field. An issue with a null lane counts toward no lane's rate. | Claiming removes the lane label, so labels cannot attribute a closed issue to a lane. |
| Q8 | The sentence stating what each cached issue carries lists `links`, and `body` for a PRD only, and no `comments`. Step 2 (*Children, per PRD*) reads a PRD's linked children from its `links`; step 5 (*Owed*) reads the PRD's prose from its cached `body`. | The cache stores what the report reads, not the raw text; a field list naming fields the cache lacks left PRDs childless. |

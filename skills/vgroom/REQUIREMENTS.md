## skills/vgroom/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| GR1 | Invoked as `/vgroom [<issue>...\|--unlabelled\|--refactor-owed]`. | |
| GR2 | One read-only subagent returns one line per issue: ready / needs-split / gone / duplicate / needs-human, plus proposed labels. | |
| GR3 | Mechanical outcomes are applied without asking: adding or removing a label, closing an issue with a reason, and editing its `Blocked by`. Nothing else is mechanical: filing a new issue (a consolidated or split one included), rewriting criteria, and any other outcome are shown to the human first and applied only on their yes. | Grooming changes queue state cheaply and reversibly on its own; new work enters the queue only with a human's yes (PR #2118 review: filing was treated as mechanical, and the grader judged the old wording both ways). |
| GR4 | A split or a criteria rewrite is shown to the human first unless they said "go". | |
| GR5 | `--refactor-owed` classifies each item GONE / FOLDS-INTO-OTHER / LIVE on `main`, consolidates the live ones into one issue per module, or one per deliverable where a module's items hold more than one, and closes the sources. | ~5–6 such items are filed per day. |
| GR6 | Near its top, the skill says it obeys `operator/PRINCIPLES.md` and reads it first. | PR #2061's prose passed GR1–GR5 without it, so no principle reached the skill. |
| GR7 | Every subagent brief the skill writes asks for a return of at most 10 lines (P6), and says that all writes stay in the project repo and that a fix belonging elsewhere is reported, not made (P11, in its words). | PR #2061's brief asked for one line per issue, unbounded, and carried no repo boundary. |
| GR9 | The skill says where `--refactor-owed` items come from, and reads the triage label set from the target repo's CLAUDE.md, naming no project fact (P12). | PR #2061 left both undefined. |
| GR10 | Before labelling an issue ready, the groom runs `$S/stale-rows.sh <issue>`. Exit 1 parks the issue with `park-issue.sh`, naming the row, the unit and the failing line it printed, and the issue is not labelled ready. Exit 0 and exit 3 go on as before, and exit 2 is reported and leaves the issue as it was. The groom never rewrites a requirement row. | A characterisation row whose unit moved on is otherwise handed out, bails at scoping, and is handed out again on every refill (#2312, #2314). |

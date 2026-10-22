## skills/veri-groom/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| GR1 | Invoked as `/veri-groom [<issue>...\|--unlabelled\|--refactor-owed]`. | |
| GR2 | One read-only subagent returns one line per issue: ready / needs-split / gone / duplicate / needs-human, plus proposed labels. | |
| GR3 | Mechanical outcomes are applied: labels, a close with a reason, `Blocked by` edits. Nothing else is mechanical: any other outcome is shown to the human first. | |
| GR4 | A split or a criteria rewrite is shown to the human first unless they said "go". | |
| GR5 | `--refactor-owed` classifies each item GONE / FOLDS-INTO-OTHER / LIVE on `main`, consolidates the live ones into one issue per module, and closes the sources. | ~5–6 such items are filed per day. |
| GR6 | Near its top, the skill says it obeys `operator/PRINCIPLES.md` and reads it first. | PR #2061's prose passed GR1–GR5 without it, so no principle reached the skill. |
| GR7 | Every subagent brief the skill writes asks for a return of at most 10 lines (P6), and says that all writes stay in the project repo and that a fix belonging elsewhere is reported, not made (P11, in its words). | PR #2061's brief asked for one line per issue, unbounded, and carried no repo boundary. |
| GR9 | The skill says where `--refactor-owed` items come from, and reads the triage label set from the target repo's CLAUDE.md, naming no project fact (P12). | PR #2061 left both undefined. |

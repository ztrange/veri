## skills/veri-groom/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| GR1 | Invoked as `/veri-groom [<issue>...\|--unlabelled\|--refactor-owed]`. | |
| GR2 | One read-only subagent returns one line per issue: ready / needs-split / gone / duplicate / needs-human, plus proposed labels. | |
| GR3 | Mechanical outcomes are applied: labels, a close with a reason, `Blocked by` fixes. | |
| GR4 | A split or a criteria rewrite is shown to the human first unless they said "go". | |
| GR5 | `--refactor-owed` classifies each item GONE / FOLDS-INTO-OTHER / LIVE on `main`, consolidates the live ones into one issue per module, and closes the sources. | ~5–6 such items are filed per day. |

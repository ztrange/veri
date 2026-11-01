# Plan for #2856 — skill-edit-step.sh exits 0 when the issue's rows sit outside a '### <unit>' under '## Requirements'

- [x] An issue body with rows under a `## <unit path>` heading and no `### <unit path>` under `## Requirements` makes `skill-edit-step.sh <issue> <unit>` exit 2 with a stderr line naming the unit and saying its rows are not under `## Requirements`, the unit file, `REQUIREMENTS.md` and GRADED unchanged (the check sits in `skill_edit_step.main` beside `_unknown_heading`; `add_ledger_step.py` untouched) ⟦criterion 1⟧
- [x] An issue body whose `## Requirements` section holds a table row under no `### ` unit heading (rows that reach no unit) makes `skill-edit-step.sh` exit 2 with a stderr line naming the problem, nothing changed ⟦criterion 2⟧
- [x] An issue body that has a `## Requirements` section but no `### <unit>` or `### <unit> (new)` for the unit the step names makes `skill-edit-step.sh` exit 2 with a stderr line naming the unit, nothing changed ⟦criterion 3⟧
- [ ] A well-formed `### <unit>` under `## Requirements` keeps `skill-edit-step.sh` exiting 0 as before, its rows applied and an author attempt passed ⟦criterion 4⟧
- [ ] An issue with no `## Requirements` section at all (a `--change`-only step) keeps `skill-edit-step.sh` exiting 0 as before ⟦criterion 4⟧
- [ ] Go-red control: with the new check removed, the first three cases fail (exit 0 instead of 2); restored, they pass ⟦human-owed⟧ ⟦criterion 5⟧

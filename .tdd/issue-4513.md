# Plan for #4513 — #4450's mutation records on skill_edit_half.py are stale on main: 5 of 11 record old text the file no longer holds

- [x] the 5 records in `.tdd/issue-4450-mutations.md` whose old text `skills/tdd/scripts/veri/skill_edit_half.py` no longer holds are retired, with the reason ⟦criterion 1⟧
- [ ] `run-finished.sh <n>` exits 1 with a `stale-pin` line for each unretired record of the run's own mutation record whose old text its mutated file in the run's worktree no longer holds ⟦criterion 2⟧

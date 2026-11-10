# Plan for #3568 — skill-edit guard counts the run's untracked .tdd/issue-<n>-pr-body.md as outside the unit

- [x] skill-edit-guard.sh <unit> <base-sha> exits 0 and prints nothing when the only untracked path besides the unit is the run's own .tdd/issue-<n>-pr-body.md, so a skill-edit author attempt in that worktree is graded (a case in skills/tdd/scripts/tests/py/test_skill_edit_guard_process.py, beside the #3045 mutation-record cases) ⟦criterion 1⟧
- [ ] skill-edit-guard.sh still exits 1 and prints the stray path, and does not print the pr-body path, when an untracked file elsewhere in the tree (not run scratch) sits next to an untracked .tdd/issue-<n>-pr-body.md (a case in skills/tdd/scripts/tests/py/test_skill_edit_guard_process.py) ⟦criterion 2⟧

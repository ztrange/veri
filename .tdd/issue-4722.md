# Plan for #4722 — test_skill_edit_step.py: one fixture installs the four stubs every case repeats

- [x] One fixture in test_skill_edit_step.py installs the `_grade`, `_author`, `event.append` and git `subprocess` stubs and the chdir and unit/list/issue tree; every case before `_next_case_2262` uses it, still 104 cases collected, all passing
- [x] Every case from `_next_case_2262` up to `test_an_as_is_marker_under_a_unit_heading_changes_neither_the_rows_nor_the_unit_apply_reads_2462` uses the fixture, still 104 cases collected, all passing
- [x] Every remaining case, `_heading_unit_case` included, uses the fixture, so `git grep -c 'setattr(skill_edit_step, "_grade"'` on the file prints at most 3 ⟦criterion 1⟧
- [x] `git grep -c 'setattr(skill_edit_step, "_author"'` on the file prints at most 3 ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] The file collects 104 cases, as on main 0568a13284, and every case passes ⟦full-suite⟧ ⟦criterion 3⟧
- [x] No file outside skills/tdd/scripts/tests/py/ changes ⟦diff-checked⟧ ⟦criterion 4⟧

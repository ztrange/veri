# Plan for #4752 — skill-edit-step.sh refuses a reworded row as a duplicate when an unescaped | in a code span truncates both rows to the same cells

- [x] `skill-edit-step.sh` given a `<reword>` row whose Requirement or Why cell differs from the held row's, both rows holding an unescaped `|` in a code span, does not exit 2 with `states the full text the unit already holds` (a case in `unit/test_skill_edit_step.py`) ⟦criterion 1⟧
- [x] `skill-edit-step.sh` exits 2 naming the row ID and the malformed cell count for an issue row that does not split into exactly ID, Requirement and Why (a case in `unit/test_skill_edit_step.py`) ⟦criterion 2⟧
- [x] `requirements-preflight.sh` exits 2 naming the row for an issue row that does not split into exactly ID, Requirement and Why, so it is refused at filing (a case in `unit/test_requirements_preflight.py`) ⟦criterion 3⟧ ⟂ refactor pending
- [ ] Go-red: with the cell-count guard removed, the malformed-row case of `unit/test_skill_edit_step.py` fails, probe `skills/tdd/scripts/veri/skill_edit_step.py` `!= 5` → `== -1` on `skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py` ⟦go-red⟧ ⟦criterion 4⟧

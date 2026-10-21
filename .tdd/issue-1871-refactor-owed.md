### SKILL.md's *Scope & plan* tells the planner to emit one skill-edit step naming the unit for each criterion that changes a unit with a requirements list, or for each unit an issue's `## Requirements` section names, and never to plan Red, Green or Refactor steps that edit such a unit; pinned by a prose case on SKILL.md ⟦criterion 1⟧
- test-only | extract the repeated `next((s for s in re.split(...)))` sentence lookup in the new case into a helper
### `SKILL-EDIT.md` says a resumed run redoes an unfinished skill-edit step from its start, with its budget reset (K9); pinned by a prose case on SKILL-EDIT.md ⟦criterion 2⟧
- test-only | hoist `_sentences(DOC.read_text(encoding="utf-8"))` in test_skill_edit_procedure.py into a shared helper or fixture

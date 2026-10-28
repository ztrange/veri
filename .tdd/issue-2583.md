# Plan for #2583 — skill-edit-step.sh --added: the refusal on a PASS unit whose issue rows only restate the list is pinned by nothing

- [x] An added skill-edit step on a unit already grading PASS, whose issue states only row IDs the unit's REQUIREMENTS.md list already carries, exits 2 naming the step and leaves REQUIREMENTS.md, the unit and GRADED unmodified, pinned by a new small case in skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py (in-process run_cli, grader and author stubbed) that fails when skill_edit_step.py's fresh is widened to bool(issue_rows); no production change ⟦criterion 1⟧
- [ ] The go-red control: with fresh widened to bool(issue_rows) the new case goes red while the _exits_3_2513 case stays green, watched by hand and restored ⟦human-owed⟧ ⟦criterion 2⟧

# Plan for #4588 — A resumed run's preflight refuses an issue-body Requirements row whose text its branch already holds under another ID

- [x] requirements-preflight.sh exits 0 for a body row whose Requirement and Why cells the unit holds under another ID, though its own ID is held with different text; a row whose text no row holds still exits 2 ⟦criterion 1⟧ ⟦criterion 3⟧
- [x] skill-edit-step.sh does not refuse that row and leaves the unit's requirements list byte-identical ⟦criterion 2⟧
- [x] ⟦skill-edit⟧ `skills/tdd/PREFLIGHT-FAILURES.md`: the requirements-preflight.sh exit 2 entry says a row the unit already holds under another ID is not a clash ⟦criterion 4⟧
- [ ] ⟦skill-edit⟧ `skills/tdd/SCRIPTS.md`: the skill-edit-step.sh entry (SC42) says a row whose text the unit holds under another ID is not a clash and is neither appended nor reworded

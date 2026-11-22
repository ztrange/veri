# Plan for #4588 — A resumed run's preflight refuses an issue-body Requirements row whose text its branch already holds under another ID

- [ ] requirements-preflight.sh exits 0 for a body row whose Requirement and Why cells the unit holds under another ID, though its own ID is held with different text; a row whose text no row holds still exits 2 ⟦criterion 1⟧ ⟦criterion 3⟧
- [ ] skill-edit-step.sh does not refuse that row and leaves the unit's requirements list byte-identical ⟦criterion 2⟧
- [ ] ⟦skill-edit⟧ `skills/tdd/PREFLIGHT-FAILURES.md`: the requirements-preflight.sh exit 2 entry says a row the unit already holds under another ID is not a clash ⟦criterion 4⟧

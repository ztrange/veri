# Plan for #2997 — An added skill-edit step that rewords existing requirement rows commits them and their regrade with no author when the prose already meets them

- [x] An `--added` skill-edit-step run whose issue rewords a listed row (same ID, different text) and whose prose already passes the reworded row exits 3, launches no author, rewrites the row in the list, regrades, and commits the list and the graded file (cases in skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py) ⟦criterion 1⟧
- [x] The same `--added` reworded-row run, with the prose already passing, appends a `skill-edit-no-author` event naming the unit ⟦criterion 2⟧
- [ ] An `--added` skill-edit-step run whose issue rows all equal the listed rows (same IDs, same text) and whose prose passes still exits 2 with "graded PASS before any author ran" and leaves the list unchanged ⟦criterion 3⟧
- [ ] An `--added` skill-edit-step run whose reworded row the prose does not meet launches the author with the reworded row's new text in its prompt, not the old text ⟦criterion 4⟧
- [ ] Go-red control: with `fresh` reverted to the new-ID-only rule, the first criterion's case goes red (exit 2); restoring it goes green ⟦human-owed⟧ ⟦criterion 5⟧

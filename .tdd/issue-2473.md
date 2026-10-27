# Plan for #2473 — A --change attempt that edits only a pin file counts as a prose change

- [x] skill_edit_step.main with `--change`, on a unit that grades PASS and at least one pin file, whose author edits only the pin file and leaves the unit byte-identical, fails the attempt with `FAIL: the author left the prose unchanged` (exit 1, no commit) instead of exiting 0 ⟦criterion 1⟧
- [x] skill_edit_step.main with `--change`, whose author changes the unit and leaves every pin file untouched, still succeeds (exit 0, the step committed), so the unit-only comparison does not count a real prose change as no change ⟦criterion 2⟧
- [x] go-red control (mutation reverting the comparison to `[unit, *pins]`: the pin-only case red, the unit-change case green) ⟦human-owed⟧ ⟦criterion 3⟧

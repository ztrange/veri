# Plan for #454 — metrics.sh's By-step table says what kind each step is, and which figure is comparable across runs

- [x] `#### By step` carries a kind column whose cell reads `pin` for a step that wrote a `pin` mark and `full` for a step that ran Red → Green → Refactor ⟦criterion 1⟧
- [x] The kind column reads `already-satisfied` for a step whose red leaf found the criterion already satisfied (a verify-pin verdict) but which carries no `pin` mark, and `full` for a full step ⟦criterion 2⟧ ⟂ refactor pending
- [ ] The kind is read off the step's own events: a step with a `pin` mark or a verify-pin verdict is short however many leaves it launched, and a full step with only two leaves in the log still reads `full` ⟦criterion 3⟧
- [ ] A report over a log of only full steps still renders the kind column, reading `full` on every row ⟦criterion 4⟧
- [ ] `#### By step` is followed by one line naming turns as the figure comparable across runs, dollars as the figure that is not, and `VERI_MODEL`, `VERI_MODEL_DEVELOPER` and `VERI_MODEL_VERIFIER` as the reason ⟦criterion 5⟧
- [ ] Every By-step column that existed before, and every other section of the report, renders the same cells for an existing log as before the kind column was added ⟦criterion 6⟧

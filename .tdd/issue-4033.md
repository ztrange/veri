# Plan for #4033 — PRD 027.11: closing the run's record is one call

- [x] `pr-finish.sh <n>` follows the port convention and refuses no argument and a missing input with exit 2 before any inner call ⟦criterion 11⟧
- [x] under `ci`, with an unchecked `⟦full-suite⟧` line and no `has no checks`, it ticks each such line and its issue criterion and commits `plan: the full suite is green on CI`; otherwise it ticks and commits nothing of the kind ⟦criterion 1⟧
- [x] it writes the `done` mark, renders and commits the metrics or carries `metrics=<code>`, checks the tree, pushes, waits on CI, writes the refactor-owed render and settles, stopping at the first call that is not clean ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 5⟧ ⟦criterion 7⟧ ⟦criterion 8⟧ ⟦criterion 9⟧ ⟦criterion 10⟧
- [x] a wait whose slice runs out exits 3 and a second call only waits again; its wait record names its conductor ⟦criterion 6⟧
- [ ] a guard fails when an inner call is a `$S/` script sub-step 2's second block does not name, and the commits, push and wait are made for real against a stub `gh` ⟦criterion 12⟧
- [ ] docs: `DRAFT-PR.md` sub-step 2's second block, `SCRIPTS.md`, rows and grades ⟦criterion 13⟧

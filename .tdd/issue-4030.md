# Plan for #4030 — PRD 027.7: the Draft PR step's branch suite is one call

- [x] `branch-gate.sh <n>` follows the port convention and refuses, exit 2 before any inner call, no argument, a missing input and an unchecked step left ⟦criterion 1⟧ ⟦criterion 10⟧
- [x] it settles `branch_suite=ci` from `branch-suite.sh`, or under `local` runs the full command through `detach-command.sh` start and wait inside the `full-suite` stage, records its time and settles `branch_suite=local`, stopping at a red wait ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 5⟧ ⟦criterion 7⟧ ⟦criterion 8⟧ ⟦criterion 9⟧
- [ ] a wait whose slice runs out exits 3 and a second call only waits again; its wait record names its conductor ⟦criterion 6⟧
- [ ] a guard fails when an inner call is a `$S/` script the opening paragraphs do not name, and the full run is made for real ⟦criterion 11⟧
- [ ] docs: `DRAFT-PR.md`'s opening, `SCRIPTS.md`, rows and grades ⟦criterion 12⟧

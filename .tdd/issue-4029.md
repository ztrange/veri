# Plan for #4029 — PRD 027.8: a step's close-out is one call

- [x] `step-close.sh <n>` follows the port convention and refuses, exit 2 before any inner call, no argument, a missing input and a refactor-half file naming another step; an `uncovered_spec=` line stops it with exit 1 before any inner call ⟦criterion 1⟧ ⟦criterion 12⟧
- [x] it runs the graded and pin checks, the refactored re-record, the tree check, the clear, commit and push, the stage end and the stop ask, stopping at the first call that is not clean ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 5⟧ ⟦criterion 9⟧ ⟦criterion 10⟧ ⟦criterion 11⟧
- [ ] it mirrors the step to the issue, decides the next step and settles `.tdd/issue-<n>-step-close` ⟦criterion 6⟧ ⟦criterion 7⟧ ⟦criterion 8⟧
- [ ] a guard fails when an inner call is a `$S/` script the Refactor loop section does not name, and the commit lands for real ⟦criterion 13⟧
- [ ] docs: sub-step 6's PASS branch, `SCRIPTS.md`, rows and grades ⟦criterion 14⟧ ⟦criterion 15⟧

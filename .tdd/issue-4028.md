# Plan for #4028 — PRD 027.6: a step's refactor is one call

- [ ] `refactor-half.sh <n>` follows the port convention and refuses, exit 2 before any inner call, no argument, a missing input, no refactor-pending step, and a red-half file naming another step ⟦criterion 1⟧ ⟦criterion 15⟧
- [ ] it asks the budget, launches `develop-refactor` under the stop check, checks the tree, the subjects and the report's flags and candidates, and names why the tidying stopped ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 10⟧ ⟦criterion 12⟧ ⟦criterion 13⟧
- [ ] it verifies blind once or records the skip, checks the tree, posts both comments, marks the log, records the leftovers and settles `.tdd/issue-<n>-refactor-half` ⟦criterion 5⟧ ⟦criterion 6⟧ ⟦criterion 7⟧ ⟦criterion 8⟧ ⟦criterion 9⟧ ⟦criterion 14⟧
- [ ] called again after an exit 3 it repeats nothing but the wait, and its wait record names its conductor ⟦criterion 11⟧
- [ ] a guard fails when an inner call is a `$S/` script the Refactor loop section does not name ⟦criterion 16⟧ ⟦criterion 17⟧
- [ ] docs: the Refactor loop section, `SCRIPTS.md`, rows and grades ⟦criterion 18⟧

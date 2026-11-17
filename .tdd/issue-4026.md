# Plan for #4026 — PRD 027.4: a step's Red half is one call

- [x] `red-half.sh <n>` follows the port convention and refuses, exit 2 before any inner call, no argument, a missing preflight file, ledger or spec, no open step, and a step of a kind RH1 excludes ⟦criterion 1⟧ ⟦criterion 16⟧
- [x] it refreshes the spec, launches `develop-red` under the stop check, waits, checks the step's cost and prints the report's three lines, stopping on `PASSES`, `UNTESTABLE` or a missing line ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 11⟧ ⟦criterion 13⟧ ⟦criterion 14⟧
- [x] it gates on the prediction, the replaced cases and the earlier steps' records, launches `verdict-red`, records the frozen tests, checks the tree, posts both comments and settles `.tdd/issue-<n>-red-half` ⟦criterion 5⟧ ⟦criterion 6⟧ ⟦criterion 7⟧ ⟦criterion 8⟧ ⟦criterion 9⟧ ⟦criterion 10⟧ ⟦criterion 15⟧
- [x] called again after an exit 3 it repeats nothing but the wait, and its wait record names its conductor ⟦criterion 12⟧
- [x] a guard fails when an inner call is a `$S/` script the Red section does not name ⟦criterion 17⟧ ⟦criterion 18⟧
- [x] docs: the Red section, `SCRIPTS.md`, rows and grades ⟦criterion 19⟧

# Plan for #4027 — PRD 027.5: a step's Green half is one call

- [x] `green-half.sh <n>` follows the port convention and refuses, exit 2 before any inner call, no argument, a missing or other-step `.tdd/issue-<n>-red-half`, and a ⟦replaces-case⟧ or ⟦ci-repair⟧ step ⟦criterion 1⟧ ⟦criterion 15⟧
- [x] it launches `develop-green` under the stop check, checks the step's cost, the suite line and the route lines, then the frozen tests, launches `verdict-green` and checks the cost again ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 5⟧ ⟦criterion 10⟧ ⟦criterion 12⟧ ⟦criterion 13⟧
- [x] on a PASS it posts both comments, runs the graded check, re-checks the frozen tests, ticks and commits, pushes, rewrites the PR body, asks for a stop and settles `.tdd/issue-<n>-green-half` ⟦criterion 6⟧ ⟦criterion 7⟧ ⟦criterion 8⟧ ⟦criterion 9⟧ ⟦criterion 14⟧
- [x] called again after an exit 3 it repeats nothing but the wait, and its wait record names its conductor ⟦criterion 11⟧
- [x] a guard fails when an inner call is a `$S/` script the Green section does not name ⟦criterion 16⟧ ⟦criterion 17⟧
- [x] docs: the Green section, `SCRIPTS.md`, rows and grades ⟦criterion 18⟧

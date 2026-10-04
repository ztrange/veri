# Plan for #816 — make test never re-enters itself: a SUITES= override cannot make a suite's nested make re-run the suite that started it

- [x] A planted re-entry — an outer `make test SUITES=<a planted fixture suite whose body runs make test TESTS=<a second fixture>>` in a scratch copy of the repo — ends with a named refusal or a bounded run instead of a growing process tree; the case runs the outer make in its own session under a process cap (ulimit -u at the current user process count plus a margin) and a deadline, kills the group by its recorded pid when the deadline passes, and fails if the deadline was reached ⟦criterion 3⟧
- [x] A nested `make test TESTS=<x>` started by a suite runs only `<x>` when the outer `make test` was given `SUITES=` on its command line ⟦criterion 1⟧
- [ ] A nested `make test TESTS=<x>` started by a suite runs only `<x>` when the outer `make test` ran with a `MAKEFLAGS` in its environment carrying `SUITES=` or `TESTS=` ⟦criterion 1⟧
- [ ] A `make test` nested deeper than a fixed bound refuses with exit 2 and a stderr line naming the depth, before running any suite ⟦criterion 2⟧
- [ ] No existing case of make-test-env.test.sh, count-line-guard.test.sh, bash-version-guard.test.sh or unit-tier.test.sh is edited or removed by the branch ⟦diff-checked⟧ ⟦criterion 4⟧
- [ ] Every existing case of make-test-env.test.sh, count-line-guard.test.sh, bash-version-guard.test.sh and unit-tier.test.sh passes ⟦full-suite⟧ ⟦criterion 4⟧

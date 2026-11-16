# Plan for #3987 — PRD 021.20: a failing case run through `make` reads as failing

- [x] a case command exiting 2 with `make: *** [test] Error 1` on stderr makes tick-ledger.sh read "case fails", exit 1 ⟦criterion 1⟧
- [x] a case command exiting 2 with `make: *** [test] Error 2` stays "never run", exit 2 ⟦criterion 2⟧
- [x] the fallback `make test TESTS=<id>` path reads make's `Error <k>` line the same way ⟦criterion 3⟧
- [x] the tick-ledger.sh entry of SCRIPTS.md states the reading, graded ⟦criterion 4⟧
- [x] the make test fallback reads a missing case file, or output saying no tests ran, as a case never run, exit 2 ⟦criterion 3⟧
- [x] only make's own last stderr line of the outermost make level picks the case code; a test's output never does, and the fallback's non-zero exit with no such line never ran ⟦criterion 1⟧

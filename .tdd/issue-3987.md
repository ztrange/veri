# Plan for #3987 — PRD 021.20: a failing case run through `make` reads as failing

- [ ] a case command exiting 2 with `make: *** [test] Error 1` on stderr makes tick-ledger.sh read "case fails", exit 1 ⟦criterion 1⟧
- [ ] a case command exiting 2 with `make: *** [test] Error 2` stays "never run", exit 2 ⟦criterion 2⟧
- [ ] the fallback `make test TESTS=<id>` path reads make's `Error <k>` line the same way ⟦criterion 3⟧
- [ ] the tick-ledger.sh entry of SCRIPTS.md states the reading, graded ⟦criterion 4⟧

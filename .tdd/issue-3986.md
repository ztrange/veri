# Plan for #3986 — PRD 021.7: `tick-ledger.sh` reads a case that could not run as exit 2

- [x] a case command exiting 126 makes tick-ledger.sh exit 2, ledger and events untouched, stderr `case <id> never run` naming the code and the command ⟦criterion 1⟧
- [ ] a case command exiting 127 does the same ⟦criterion 1⟧
- [ ] a case command exiting 137 does the same ⟦criterion 2⟧
- [ ] a case command exiting 3 still reads as "case fails", exit 1 ⟦criterion 3⟧
- [ ] the tick-ledger.sh entry of SCRIPTS.md states the mapping, graded ⟦criterion 4⟧

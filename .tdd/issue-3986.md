# Plan for #3986 — PRD 021.7: `tick-ledger.sh` reads a case that could not run as exit 2

- [x] a case command exiting 126 makes tick-ledger.sh exit 2, ledger and events untouched, stderr `case <id> never run` naming the code and the command ⟦criterion 1⟧
- [x] a case command exiting 127 does the same ⟦criterion 1⟧
- [x] a case command exiting 137 does the same ⟦criterion 2⟧
- [x] a case command exiting 3 still reads as "case fails", exit 1 ⟦criterion 3⟧
- [x] the tick-ledger.sh entry of SCRIPTS.md states the mapping, graded ⟦criterion 4⟧
- [x] a case command Python reports killed by a signal (a negative code) never ran, exit 2, stderr naming the signal, on both command paths ⟦criterion 2⟧
- [x] a recipe command make itself could not execute (its own No such file or directory / Permission denied line, reported as Error 1) is a case never run, exit 2 ⟦criterion 1⟧

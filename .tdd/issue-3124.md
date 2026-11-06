# Plan for #3124 — pin-recheck exits 2 when a pin's recorded command cannot run

- [x] `pin-recheck.sh` exits 2, naming the pin file and the recorded command on stderr, when a pin's recorded command is not found (its unmutated run exits 127), instead of printing `needs a look`; pinned by one process case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py ⟦criterion 1⟧
- [x] `pin-recheck.sh` exits 2, naming the pin file and the recorded `make` command on stderr, when that `make` command reports no makefile on its unmutated run, instead of printing `needs a look`; pinned by one process case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py ⟦criterion 1⟧
- [ ] An ordinary failing unmutated run — a `make` command whose makefile exists but whose target fails — still prints `needs a look: <file>` on stdout and exits 0, never exit 2; pinned by one process case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py ⟦criterion 1⟧
- [ ] Go-red control: with the new exit-2 branch removed on purpose, the not-found case goes red; restored, it passes ⟦human-owed⟧ ⟦criterion 2⟧
- [ ] skills/tdd/SCRIPTS.md: the `pin-recheck.sh` entry says it exits 2, naming the pin file and command, when a pin's recorded command cannot run (not found, or `make` with no makefile), and prints `needs a look` for an ordinary red base run (SC74) ⟦skill-edit⟧

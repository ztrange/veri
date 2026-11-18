# Plan for #4298 — tick_ledger.run_case returns its command; no module globals

- [ ] `run_case` returns the command it ran and the process exit code with its answer, and the "never run" complaint is built from that return value ⟦criterion 3⟧
- [ ] `run_case` has no `global` statement ⟦criterion 2⟧
- [ ] `tick_ledger.py` declares no module-level `LAST_COMMAND` or `LAST_CODE` ⟦criterion 1⟧
- [ ] every message, exit code and file `tick-ledger.sh` produces is unchanged and the full suite is green ⟦full-suite⟧ ⟦criterion 4⟧

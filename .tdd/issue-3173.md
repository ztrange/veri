# Plan for #3173 — ready-check checks the default ready-for-agent label when VERI_LABEL is unset

- [ ] With `VERI_LABEL` unset and a repository whose labels include `ready-for-agent`, `ready-check.sh` prints its label row as `ok` naming `ready-for-agent` (a medium case with a real process, in `skills/tdd/scripts/tests/py/test_ready_check_process.py`) ⟦criterion 1⟧
- [ ] With `VERI_LABEL` unset and `ready-for-agent` missing from the repository's labels, `ready-check.sh` prints its label row as a `fail` line naming `ready-for-agent` (a medium case with a real process, in `skills/tdd/scripts/tests/py/test_ready_check_process.py`) ⟦criterion 1⟧
- [ ] With `VERI_LABEL` set but empty, `ready-check.sh` prints its label row as a `fail` line saying to name a label or leave `VERI_LABEL` unset, never ``create the `` label`` (a medium case with a real process, in `skills/tdd/scripts/tests/py/test_ready_check_process.py`) ⟦criterion 2⟧

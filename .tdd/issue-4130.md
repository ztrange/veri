# Plan for #4130 — PRD 023.10: a shim reads the venv's version from pyvenv.cfg

- [x] tests/py/test_shim_pyvenv_cfg_process.py: with `version = 3.14.7` in the venv's `pyvenv.cfg`, a venv `python3` stub that says 3.9.6 when asked and runs the real interpreter otherwise, and a PATH `python3` that exits 9, the shim exits with its module's code and stdout, not 2 ⟦criterion 1⟧
- [ ] tests/py/test_shim_pyvenv_cfg_process.py: a venv whose `pyvenv.cfg` version is below the floor is passed over, and when no interpreter qualifies the shim exits 2 with today's two stderr lines, the venv's naming the version `pyvenv.cfg` gave ⟦criterion 3⟧
- [ ] tests/py/test_shim_pyvenv_cfg_process.py: a venv with no `pyvenv.cfg`, or one with no parseable `version` line, is checked by running its `python3` ⟦criterion 2⟧
- [ ] the cases of test_shim_interpreter_floor_process.py, test_shim_interpreter_guard_process.py and test_shims_process.py pass unchanged ⟦criterion 4⟧

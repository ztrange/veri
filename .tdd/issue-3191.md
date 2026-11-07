# Plan for #3191 — make test goes red when PATH's python3 is below the 3.12 floor: two cases run their probe on it, unchecked

- [x] With the venv healthy and PATH's `python3` older than the 3.12 floor, the pytest leg (`skills/tdd/scripts/veri/pytest_leg.py`, which `make test` and `make unit` launch) refuses with exit 2 before any suite runs, its stderr naming PATH's `python3` interpreter and its version ⟦criterion 1⟧
- [ ] With the venv first on PATH, the `test_detach_command_process.py` signal case and `test_1463_wait_leaf_returns_the_verdict_the_stub_verifier_gave_through_the_real_chain` still pass in the full suite ⟦full-suite⟧ ⟦criterion 2⟧
- [ ] The `test_detach_command_process.py` signal case is watched going red when `detach-command.sh start` stops ignoring SIGINT, then restored ⟦human-owed⟧ ⟦criterion 2⟧

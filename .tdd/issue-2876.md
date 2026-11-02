# Plan for #2876 — pin-recheck reads a command that ran no test as a pin that stayed green

- [x] A mutation record whose command is `bash -c` with its script unquoted, so only its first word runs and exits 0 without running any test, is reported `needs a look` on stdout and pin-recheck.sh exits 0, not 1 (a medium case with a real process, in skills/tdd/scripts/tests/py/test_pin_recheck_process.py) ⟦criterion 1⟧ ⟂ refactor pending
- [ ] A mutation record whose command runs its test, passes clean and fails mutated still reports the pin as held: no `needs a look` line, no stayed-green line, exit 0 (a medium case with a real process, in skills/tdd/scripts/tests/py/test_pin_recheck_process.py) ⟦criterion 2⟧
- [ ] A mutation record whose command reads the pinned file, passes clean and also passes mutated still reports `pin stayed green under its mutation` and pin-recheck.sh exits 1 (a medium case with a real process, in skills/tdd/scripts/tests/py/test_pin_recheck_process.py) ⟦criterion 3⟧
- [ ] After the control run of a record whose command runs no test, the pinned file holds its original content byte for byte (a medium case with a real process, in skills/tdd/scripts/tests/py/test_pin_recheck_process.py) ⟦criterion 4⟧
- [ ] When a record's mutated run fails, no control run is made: the command is never run against the pinned file's control content (a medium case with a real process, in skills/tdd/scripts/tests/py/test_pin_recheck_process.py) ⟦criterion 4⟧
- [ ] The control run is named in skills/tdd/scripts/veri/pin_recheck.py's code ⟦diff-checked⟧ ⟦criterion 4⟧
- [ ] A mutation record whose command is not `bash -c` and runs no test (`true`) is reported `needs a look` and pin-recheck.sh exits 0 (a medium case with a real process, in skills/tdd/scripts/tests/py/test_pin_recheck_process.py) ⟦criterion 5⟧
- [ ] Control-run control: with the control run removed, criterion 1's case goes red; restore it ⟦human-owed⟧ ⟦criterion 6⟧

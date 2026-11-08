# Plan for #3346 — restart-conductor.sh keeps watching a run whose conductor log holds non-JSON lines

- [x] restart_conductor fed a conductor-<n>.log in the on-disk shape (a leading plain-text line such as `update-veri.sh: already current`, then stream-json records) keeps watching and measures growth from the JSON records alone, the plain-text line skipped (a small unit case in tests/py/unit/test_restart_conductor.py) ⟦criterion 1⟧
- [x] restart_conductor fed a conductor-<n>.log whose every line is non-JSON measures no growth and keeps watching, stopping nothing (a small unit case in tests/py/unit/test_restart_conductor.py) ⟦criterion 2⟧
- [ ] Go-red: with the non-JSON skip removed from `_growth`, both new cases go red ⟦human-owed⟧ ⟦criterion 3⟧
- [ ] The existing cases that write conductor-7.log as pure JSONL still pass ⟦full-suite⟧ ⟦criterion 4⟧
- [x] restart_conductor exits 2 with a stderr line naming conductor-<n>.log when that log exists but cannot be read (for example it is a directory) (a small unit case in tests/py/unit/test_restart_conductor.py)

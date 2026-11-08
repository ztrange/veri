# Plan for #3298 — restore_production_files raises FileNotFoundError when a red leaf deletes a snapshotted file; no case pins an untouched clean file

- [ ] A red leaf that deletes a snapshotted (uncommitted, modified) tracked production file has it written back with its pre-leaf bytes, a `production-file-restored` event naming the file is marked, and the supervisor exits with the leaf's own exit code rather than raising FileNotFoundError (a process case in skills/tdd/scripts/tests/py/test_supervise_process.py) ⟦criterion 1⟧
- [ ] A clean, unmodified tracked production file that a red leaf does not touch is left byte-identical and gets no `production-file-restored` event (a process case in skills/tdd/scripts/tests/py/test_supervise_process.py) ⟦criterion 2⟧

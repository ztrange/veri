### tick-ledger.sh given a directory as its ledger exits 2, with one stderr line naming the path and the reason and no traceback ⟦criterion 1⟧
- out-of-scope | extract the shared "<script>.sh: <path>: <strerror>" stderr line (tick_ledger.py:20, add_ledger_step.py:69, preserve_attempt.py:75, refactor_owed.py:53, run_verdict.py:15, workqueue.py:158) into one helper in the veri package
### tick-ledger.sh given a ledger path that does not exist exits 2, with one stderr line naming the path and no traceback ⟦criterion 2⟧
- test-only | fold tick-ledger.test.sh's directory-ledger and absent-ledger cases (L34–46), which repeat the same run / one-stderr-line / names-path / no-Traceback assertion, into one helper that takes the path and an extra stderr pattern
- test-only | parametrize test_tick_ledger.py's missing-ledger and directory-ledger tests (L125–138) over (path, strerror), since they differ only in those two values

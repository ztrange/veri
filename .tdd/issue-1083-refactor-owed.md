### tick-ledger.sh given a directory as its ledger exits 2, with one stderr line naming the path and the reason and no traceback ⟦criterion 1⟧
- out-of-scope | extract the shared "<script>.sh: <path>: <strerror>" stderr line (tick_ledger.py:20, add_ledger_step.py:69, preserve_attempt.py:75, refactor_owed.py:53, run_verdict.py:15, workqueue.py:158) into one helper in the veri package

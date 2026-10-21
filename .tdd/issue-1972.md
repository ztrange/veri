# Plan for #1972 — The ledger module reads and writes the ledger file; its entry points stop doing their own I/O

- [ ] tick-ledger.sh ticks a step in a ledger holding a NUL byte and a non-UTF-8 byte: it exits 0, the NUL is dropped and the non-UTF-8 byte survives the rewrite unchanged ⟦criterion 1⟧
- [ ] add-ledger-step.sh inserts a step into a ledger holding a NUL byte and a non-UTF-8 byte: it exits 0, the NUL is dropped and the non-UTF-8 byte survives the rewrite unchanged ⟦criterion 1⟧
- [ ] reorder-ledger-steps.sh moves a step in a ledger holding a NUL byte and a non-UTF-8 byte: it exits 0, the NUL is dropped and the non-UTF-8 byte survives the rewrite unchanged ⟦criterion 1⟧
- [ ] clear-refactor-pending.sh clears a step's pending mark in a ledger holding a NUL byte and a non-UTF-8 byte: it exits 0, the NUL is dropped and the non-UTF-8 byte survives the rewrite unchanged ⟦criterion 1⟧
- [ ] add-ledger-step.sh replaces the ledger atomically: when its write fails, the original ledger is left byte-identical and no temporary file is left beside it ⟦criterion 2⟧
- [ ] add-ledger-step.sh exits 2 and names the temporary file on stderr when a failed write leaves that temporary file behind ⟦criterion 3⟧
- [ ] reorder-ledger-steps.sh exits 2 and names the temporary file on stderr when a failed write leaves that temporary file behind ⟦criterion 3⟧
- [ ] tick-ledger.sh exits 2 and names the temporary file on stderr when a failed write leaves that temporary file behind ⟦criterion 3⟧
- [ ] clear-refactor-pending.sh exits 2 and names the temporary file on stderr when a failed write leaves that temporary file behind ⟦criterion 3⟧
- [ ] reorder-ledger-steps.sh exits 2 with the ledger path and the OS reason on stderr when the ledger path is unreadable (a directory) ⟦criterion 4⟧
- [ ] add-ledger-step.sh exits 2 with the ledger path and the OS reason on stderr when the ledger path is unreadable (a directory) ⟦criterion 4⟧
- [ ] tick-ledger.sh exits 2 with the ledger path and the OS reason on stderr when the ledger path is unreadable (a directory) ⟦criterion 4⟧
- [ ] clear-refactor-pending.sh exits 2 with the ledger path and the OS reason on stderr when the ledger path is unreadable (a directory) ⟦criterion 4⟧
- [ ] the four entry points (tick_ledger.py, add_ledger_step.py, reorder_ledger_steps.py, clear_refactor_pending.py) open no ledger file themselves: ledger.py holds the one ledger reader and the one atomic writer with its LeftBehind and OSError handling, and clear_refactor_pending.py's dead non-bool branch (`to_contract`) is gone; no production behaviour changes ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] every existing case in tests/py/unit/test_tick_ledger.py, tests/py/test_tick_ledger_process.py, tests/py/unit/test_add_ledger_step.py, tests/py/test_add_ledger_step_process.py, tests/py/unit/test_reorder_ledger_steps.py, tests/py/unit/test_clear_refactor_pending.py and tests/py/test_clear_refactor_pending_process.py keeps its name and its outcome: the branch's diff renames and deletes none of them and changes no assertion in them ⟦diff-checked⟧ ⟦criterion 5⟧

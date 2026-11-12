# Plan for #3729 — Cover the behaviour #3711 refactors

- [x] With subprocess.Popen replaced by an in-process spy and the log path in tmp_path, restart_conductor.detach_leaf("<n>") launches exactly one process whose argv is [<scripts>/detach-leaf.sh, <scripts>/run-conductor.sh, "<n>"], where <scripts> is the real skills/tdd/scripts directory holding restart-conductor.sh; a small unit case in skills/tdd/scripts/tests/py/unit/test_restart_conductor.py, no production change, that goes red when the scripts-directory expression in detach_leaf loses one dirname ⟦criterion 1⟧

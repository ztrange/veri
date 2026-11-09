# Plan for #3247 — watch-runs.sh prints 'exited <n>' for a conductor that is still alive

- [x] With a live conductor whose conductor.pid has two lines (the pid, then its start-time line), watch-runs.sh prints no exit line for that issue while the pid answers kill -0 (a case in tests/py/unit/test_watch_runs.py) ⟦criterion 1⟧ ⟂ refactor pending
- [ ] watch-runs.sh never prints an `exited` line whose state is `running`: an issue whose run state reads `running` is not reported exited (a case in tests/py/unit/test_watch_runs.py) ⟦criterion 2⟧

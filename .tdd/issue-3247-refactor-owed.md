### watch-runs.sh never prints an `exited` line whose state is `running`: an issue whose run state reads `running` is not reported exited (a case in tests/py/unit/test_watch_runs.py) ⟦criterion 2⟧
- `run_state(issue).split(" ")[0]` appears twice in `watch_runs.py:main`, once before the loop and once inside it. This cycle did not write the first copy, so I left it alone.

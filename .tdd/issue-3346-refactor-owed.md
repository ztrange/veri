### restart_conductor exits 2 with a stderr line naming conductor-<n>.log when that log exists but cannot be read (for example it is a directory) (a small unit case in tests/py/unit/test_restart_conductor.py)
- test-only | extract the repeated conductor_alive/run_state/stop_run/detach_leaf/sleep monkeypatch block in test_restart_conductor.py into a shared helper

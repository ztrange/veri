### With no `.tdd/report-cache.json` snapshot, Queue says there is no snapshot while Landed, Running and Waiting still print ⟦criterion 3⟧
- test-only | in test_status_report.py, extract the repeated `("Landed", "Running", "Queue", "Waiting")` tuple and the `status` import and `main_working_tree` monkeypatch setup into a shared constant and fixture
### An empty Landed, Running or Waiting section keeps its heading and says "none" ⟦criterion 1⟧
- test-only | the three `test_2750_report_*` cases in `test_status_report.py` repeat the same setup (`importlib.import_module("veri.status")`, the `main_working_tree` monkeypatch, and `run_cli(status, ["--report"])`), which could become one fixture
### Landed leaves out a tag cut before the time in `.tdd/status-last` ⟦criterion 1⟧
- out-of-scope | merge the two `git tag --list` calls in `landed_lines` into one call, and update the `fake_tags` stub in `tests/py/unit/test_status_report.py` to the new `<unix-time> <name>  <subject>` output format
### Running lists one block headed `#<n>` for each run whose journal (`$VERI_HOME/runs/<owner>-<repo>/<n>.jsonl`) holds a `conductor-start` event whose `pid` answers `kill -0` with a start time matching its `started` ⟦criterion 1⟧
- test-only | extract the repeated repo, origin-config and journal setup in the two `test_status_report_running.py` cases into a shared helper or fixture
### Running leaves out a run whose journal's `conductor-start` pid is dead or whose start time does not match `started` ⟦criterion 1⟧
- rename `first` in `running_lines` to `start`, since it holds the latest `conductor-start` and not the first
- extract the `since` parse in `landed_lines` and the pid/start-time liveness check in `running_lines` into named helpers
### Running's awake wall time for a run is its journal's last event's `awake` minus its first event's `awake` ⟦criterion 5⟧
- test-only | The Running test files (`test_status_report_running*.py`) each repeat the same fixture setup: a fake `.git` config, `VERI_HOME`, a journal write and `subprocess.run` stubs. A shared helper or fixture would remove that duplication.
### Running's cost carries its delta since the time in `.tdd/status-last`: the cost of the run's journal events after that time ⟦criterion 1⟧
- `running_lines` repeats the `sum(... if e["ts"] > since)` delta pattern for steps and cost; extract a small helper
### After a report printed, `.tdd/status-last` holds the report's time and its queue counts ⟦criterion 7⟧
- the `%Y-%m-%dT%H:%M:%SZ` timestamp format is repeated in three places in `status.py`, two of them older code this cycle did not write. A shared constant would also change code outside this cycle.
not-done | transform-rejected | merge the two `git tag --list` calls in `landed_lines` into one call, and update the `fake_tags` stub in `tests/py/unit/test_status_report.py` to the new `<unix-time> <name>  <subject>` output format
applied | 0e5004d8bfa0e1c48a47ca12672edfe315b94c62 | rename `first` in `running_lines` to `start`, since it holds the latest `conductor-start` and not the first	refactor: rename first to start in running_lines (#2750)

### With no `.tdd/report-cache.json` snapshot, Queue says there is no snapshot while Landed, Running and Waiting still print ⟦criterion 3⟧
- test-only | in test_status_report.py, extract the repeated `("Landed", "Running", "Queue", "Waiting")` tuple and the `status` import and `main_working_tree` monkeypatch setup into a shared constant and fixture
### An empty Landed, Running or Waiting section keeps its heading and says "none" ⟦criterion 1⟧
- test-only | the three `test_2750_report_*` cases in `test_status_report.py` repeat the same setup (`importlib.import_module("veri.status")`, the `main_working_tree` monkeypatch, and `run_cli(status, ["--report"])`), which could become one fixture

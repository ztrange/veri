### With no `.tdd/report-cache.json` snapshot, Queue says there is no snapshot while Landed, Running and Waiting still print ⟦criterion 3⟧
- test-only | in test_status_report.py, extract the repeated `("Landed", "Running", "Queue", "Waiting")` tuple and the `status` import and `main_working_tree` monkeypatch setup into a shared constant and fixture

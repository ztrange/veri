# Plan for #1977 — stop-reason, supervise, wrong-test-route and run-conductor read events.jsonl through event_log

- [x] Given an events log holding a line that is not JSON, stop-reason.sh exits with the code it exits with today, no production change (a pin, in the stop-reason suites) ⟦criterion 2⟧
- [x] supervise.sh's red-awaits-pass answer skips a line of the events log that is not JSON and still reads the launch and verdict lines after it, no production change (a pin, in the supervise suite) ⟦criterion 3⟧
- [x] wrong-test-route.sh's rerouted answer skips a line of the events log that is not JSON and still finds a reroute event for the step on a line after it, no production change (a pin, in the wrong-test-route suite) ⟦criterion 3⟧
- [x] run-conductor.sh treats a run whose last non-blank event is done, bail or stop as closed, and a run whose last non-blank event is any other event as open, no production change (a pin, in the run-conductor suite) ⟦criterion 4⟧
- [x] No module under skills/tdd/scripts/veri/ except event.py and event_log.py opens events.jsonl: stop_reason, supervise, wrong_test_route and run_conductor read the log through event_log.read_events, each keeping its own answer and its own rule for when a run has ended ⟦criterion 5⟧
- [x] Every existing case in tests/py/unit/test_stop_reason.py, tests/py/test_stop_reason_process.py, tests/py/test_supervise.py, tests/py/unit/test_wrong_test_route.py and tests/py/test_run_conductor.py keeps its name and its outcome ⟦diff-checked⟧ ⟦criterion 1⟧

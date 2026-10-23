# Plan for #2035 — read_events raises UnicodeDecodeError on a non-UTF-8 byte in events.jsonl, outside its own skip

- [x] read_events with its default errors="replace" over a log one of whose lines holds a byte that does not decode as UTF-8 never raises and returns that line with U+FFFD in place of each bad byte, whether or not skip_unreadable is set (an in-process unit case in tests/py/unit/test_event_log.py) ⟦criterion 1⟧
- [x] read_events by default refuses a line that is not a JSON object with a ValueError whose message names the log's path (an in-process unit case in tests/py/unit/test_event_log.py) ⟦criterion 1⟧
- [ ] read_events called with errors="strict" over a log one of whose lines does not decode as UTF-8 keeps raising UnicodeDecodeError, whether or not skip_unreadable is set, which step_cost.py relies on to exit 2 (an in-process unit case in tests/py/unit/test_event_log.py) ⟦criterion 1⟧
- [ ] parallel-conductors.sh report over a run whose events.jsonl holds one non-UTF-8 byte prints that run's line and exits 0 (a case in tests/py/test_parallel_conductors.py) ⟦criterion 2⟧

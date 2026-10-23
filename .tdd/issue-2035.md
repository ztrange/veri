# Plan for #2035 — read_events raises UnicodeDecodeError on a non-UTF-8 byte in events.jsonl, outside its own skip

- [ ] read_events called with errors="strict" and skip_unreadable=True over a log one of whose lines holds a byte that does not decode as UTF-8 skips that line and returns the other lines' events in order, raising nothing (an in-process unit case in tests/py/unit/test_event_log.py) ⟦criterion 1⟧
- [ ] read_events by default refuses a line that is not a JSON object with a ValueError whose message names the log's path (an in-process unit case in tests/py/unit/test_event_log.py) ⟦criterion 1⟧
- [ ] read_events called with errors="strict" and neither skip_unreadable nor mark_unreadable over a log one of whose lines does not decode as UTF-8 raises a ValueError whose message names the log's path, the same refusal a non-object line gets, never letting it escape from reading the file (an in-process unit case in tests/py/unit/test_event_log.py) ⟦criterion 1⟧
- [ ] parallel-conductors.sh report over a run whose events.jsonl holds one non-UTF-8 byte prints that run's line and exits 0 (a case in tests/py/test_parallel_conductors.py) ⟦criterion 2⟧

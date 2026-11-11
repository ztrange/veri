# Plan for #3661 — dispatch.sh reports a live run as stalled when its leaf writes only to its .tdd/*.log

- [x] dispatch.sh does not print `stalled <n>` for a run whose `events.jsonl`, `conductor-<n>.log` and `.tdd/*.out` are all older than `VERI_DISPATCH_STALL` but whose leaf log `.tdd/<leaf>.log` was written within it (a small unit case in tests/py/unit/test_dispatch.py, driven in-process, failing on the current code) ⟦criterion 1⟧
- [ ] dispatch.sh still prints `stalled <n>` for a run whose `events.jsonl`, `conductor-<n>.log`, `.tdd/*.out` and `.tdd/<leaf>.log` are all older than `VERI_DISPATCH_STALL` (a small unit case in tests/py/unit/test_dispatch.py, driven in-process) ⟦criterion 2⟧

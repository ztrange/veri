# Plan for #3360 — dispatch.sh reports a live run stalled while it waits on its full suite

- [x] A live run whose `.tdd/events.jsonl` is older than `VERI_DISPATCH_STALL` but whose conductor log `.tdd/conductor-<issue>.log` is newer is not reported `stalled` by `dispatch.sh` (a case in skills/tdd/scripts/tests/py/unit/test_dispatch.py, failing on the current code) ⟦criterion 1⟧
- [x] A live run whose `.tdd/events.jsonl` is older than `VERI_DISPATCH_STALL` but whose detached command's output file `.tdd/<name>.out` is newer is not reported `stalled` by `dispatch.sh` (a case in skills/tdd/scripts/tests/py/unit/test_dispatch.py) ⟦criterion 1⟧
- [x] A live run whose events log, conductor log and detached-command output files are all older than `VERI_DISPATCH_STALL` is still reported `stalled <issue>` by `dispatch.sh` (a case in skills/tdd/scripts/tests/py/unit/test_dispatch.py) ⟦criterion 2⟧

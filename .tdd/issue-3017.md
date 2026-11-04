# Plan for #3017 — pin-recheck replays every issue's before-state records, not only those whose test file the range touches

- [x] pin-recheck.sh over a range that touches no recorded file and no `before` record's `keep` file does not replay that `before` record (its command never runs) and exits 3, nothing in scope; pinned by a medium (real git, real process) case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py ⟦criterion 1⟧
- [x] pin-recheck.sh over a range whose diff touches a `before` record's `keep` file still replays that record, and when the command stays green on the before-state it exits 1 naming the keep file on stderr; pinned by a medium (real git, real process) case in skills/tdd/scripts/tests/py/test_pin_recheck_process.py ⟦criterion 2⟧
- [ ] Go-red control: with the filter in skills/tdd/scripts/veri/pin_recheck.py restored to keep `before` records unconditionally, the first step's case goes red — a manual check recorded by a human ⟦human-owed⟧ ⟦criterion 3⟧

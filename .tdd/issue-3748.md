# Plan for #3748 — dispatch.sh re-reads an empty queue every 2 s while a slot is free, spending the GitHub quota

- [ ] With a fake clock and a fake `solvable_issues` returning an empty queue, a free slot and one live conductor, dispatch calls `solvable_issues` once across ticks spanning less than `VERI_DISPATCH_OVERLAP_POLL` seconds, then again once that interval has passed (a small in-process case in `skills/tdd/scripts/tests/py/unit/test_dispatch.py`) ⟦criterion 1⟧

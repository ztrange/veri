# Plan for #2635 — watch-runs.sh and status.sh tolerate non-JSON lines in a leaf log instead of exiting 2

- [x] watch-runs keeps watching, with no exit 2 and no traceback, when the run's newest leaf log under its .tdd holds stream-json lines followed by blank and plain-text prose lines, and reports that run's exit normally once its conductor exits; reproduced by a small in-process unit case in skills/tdd/scripts/tests/py/unit/test_watch_runs.py ⟦criterion 1⟧
- [x] watch-runs keeps watching, with no exit 2 and no traceback, when the run's newest leaf log holds only a partial first line, and reports that run's exit normally once its conductor exits; reproduced by a small in-process unit case in skills/tdd/scripts/tests/py/unit/test_watch_runs.py ⟦criterion 1⟧
- [x] status --json renders, without raising and exiting 0, a run whose newest leaf log holds stream-json lines followed by blank and plain-text prose lines; reproduced by a case in the status suite with the same fixture ⟦criterion 2⟧
- [x] status --json renders, without raising and exiting 0, a run whose newest leaf log holds only a partial first line; reproduced by a case in the status suite with the same fixture ⟦criterion 2⟧
- [ ] Go-red control: with the fix reverted, the prose-lines case goes red — watched red by hand and restored ⟦human-owed⟧ ⟦criterion 3⟧

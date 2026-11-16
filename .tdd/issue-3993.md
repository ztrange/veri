# Plan for #3993 — PRD 021.19: `workqueue.sh` names the holder of a lock it cannot take

- [x] taking the lock writes the taker's pid and start time to `.tdd/workqueue.lock/holder` in `pid_file.record`'s form, and release removes it with the directory; a small case in `tests/py/unit/test_workqueue.py` ⟦criterion 1⟧
- [x] a take that gives up on a lock whose holder file names a live pid exits 2 with `could not take the lock <path>` and that pid with `alive`; a small case in `tests/py/unit/test_workqueue.py` ⟦criterion 2⟧
- [x] a take that gives up on a lock whose holder file names a dead pid prints that pid with `dead`; a small case in `tests/py/unit/test_workqueue.py` ⟦criterion 2⟧
- [x] a take that gives up on a lock with no holder file prints `unrecorded`; a small case in `tests/py/unit/test_workqueue.py` ⟦criterion 2⟧
- [x] the `workqueue.sh` entry of `skills/tdd/scripts/veri/README.md` states both ⟦criterion 3⟧

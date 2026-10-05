# Plan for #898 — workqueue.sh resolves an empty git toplevel to /.tdd/workqueue, so test_workqueue.py's outside-a-repository case reads the real filesystem root

- [x] A test with a fake filesystem root (a monkeypatched path, never the real `/`) holding a `.tdd/workqueue` with a queued line for the worker pins that `show`, `next` and `assign` with an empty toplevel read, lock and write nothing under that root — failing on today's code, which reads that queue, prints the worker's line and appends to it ⟦criterion 2⟧
- [x] With `git worktree list` answering an empty toplevel, `workqueue.sh show` exits 2 with empty stdout and a stderr line saying it is outside a repository ⟦criterion 1⟧
- [x] When `git worktree list` fails with no output, `workqueue.sh show` exits 2 with empty stdout and the same outside-a-repository stderr line ⟦criterion 1⟧
- [x] With an empty toplevel, `workqueue.sh next <worker>` exits 2 with empty stdout and the outside-a-repository stderr line instead of raising FileNotFoundError (the existing case's FileNotFoundError expectation is replaced by this one) ⟦criterion 1⟧
- [x] With an empty toplevel, `workqueue.sh assign <worker> <issue>` exits 2 with empty stdout and the outside-a-repository stderr line ⟦criterion 1⟧
- [x] With an empty toplevel, `start`, `done` and `park` each exit 2 with empty stdout and the outside-a-repository stderr line, taking no lock ⟦criterion 1⟧
- [x] The outside-a-repository part of the existing assign case reads and writes nothing outside `tmp_path` and passes whatever the uid and whether or not `/.tdd/workqueue` exists, never skipped when uid is 0 ⟦criterion 3⟧
- [ ] fix the full-suite failure: no-permission-bits.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ forces a read or write failure through permission bits (#846): test_workqueue.py:569 and :609 match its system-path rule on their "/.tdd" literals ⟦suite-repair⟧ ⟦criterion 3⟧

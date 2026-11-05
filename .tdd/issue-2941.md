# Plan for #2941 — Nothing pins test_ignored_signals_process's signal and detach-leaf waits to CHILD_SESSION_WAIT, so a literal timeout=25 passes every test

- [x] An unmarked (small) case in skills/tdd/scripts/tests/py/test_ignored_signals_process.py parses that module's own source and asserts that every subprocess.run call in it passes timeout=CHILD_SESSION_WAIT (the name, not a literal), for each call site, the signal, detach-leaf and HUP-order sites included, so a literal timeout=25 at any one of them turns it red; no production change ⟦criterion 1⟧
- [ ] The guard, broken on purpose (a literal timeout=25 at the signal site, then at the detach-leaf site), goes red each time ⟦human-owed⟧ ⟦criterion 2⟧

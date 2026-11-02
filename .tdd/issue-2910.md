# Plan for #2910 — test_ignored_signals_process's child-session wait is a fixed 25 s, so a loaded machine red-baselines unrelated runs

- [ ] The three child-session waits in test_ignored_signals_process.py (the signal case, the detach-leaf case and the HUP-order case) share one named module-level bound, greater than 25 s and less than conftest's PROCESS_CASE_TIMEOUT (90 s), pinned by a small unmarked case in that file asserting the bound's range against PROCESS_CASE_TIMEOUT; a test-only change, no production code ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] The HUP-order case's child-session wait, when its child outlives the shared bound, fails the case with a message naming the wait, as the signal and detach-leaf cases' waits do, pinned by a process case that shrinks the bound and runs a child that sleeps past it; a test-only change, no production code ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] The guard, broken on purpose (bound set back to 25), goes red ⟦human-owed⟧ ⟦criterion 3⟧

# Plan for #4415 — The supervisor reads a full-run-lock wait marker once, so a marker its waiter removes mid-check never crashes the leaf

- [ ] lock_waiting takes the waiter's start time from the one read, so a marker removed after the read reads as not waiting, never raises ⟦criterion 1⟧
- [ ] a marker removed before the read still reads as not waiting ⟦criterion 2⟧
- [ ] lock_waiting takes the waiter's pid from the one read too, so a marker rewritten after the read is judged by what was read ⟦criterion 3⟧

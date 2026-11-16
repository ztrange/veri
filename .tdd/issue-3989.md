# Plan for #3989 — PRD 021.9: a dead waiter's lock-wait marker never freezes a supervisor

- [ ] `full_run_lock.acquire`, marking a wait, writes its pid on line 1 and its start time on line 2 of the marker, in `pid_file.record`'s form ⟦criterion 1⟧
- [ ] a supervisor whose marker names a dead pid ignores it and its hard timeout, shrunk by `VERI_TIMEOUT`, fires ⟦criterion 2⟧
- [ ] a marker naming a live pid under a different start time is ignored too ⟦criterion 2⟧
- [ ] an empty marker still freezes the supervisor's timers ⟦criterion 3⟧
- [ ] veri/README.md's `acquire()` entry says the marker names the waiter and a dead waiter's marker is ignored ⟦criterion 4⟧
- [ ] CLAUDE.md's full-run lock paragraph says the same (CM159), graded ⟦criterion 5⟧

# Plan for #4454 — PRD 036.7: load timeouts lower T

- [x] a leg that claimed its workers appends `<epoch> <pid> <test file> <node id> <workers>` to VERI_TEST_TIMEOUTS_FILE per case its per-case timeout fails, and records a `case-timeout` event (`nodeid`, `workers`) ⟦criterion 1⟧
- [x] a leg run with VERI_PYTEST_WORKERS exported appends nothing to the timeouts file and lowers nothing ⟦criterion 11⟧
- [x] a timeout appended while the timeouts file holds a line from another test file within VERI_LOAD_WINDOW writes VERI_TEST_LOAD_FILE (through a temporary file) with T-2 on line 1 and the time on line 2 ⟦criterion 4⟧
- [x] timeouts from one test file only, however many, write no load file ⟦criterion 2⟧
- [x] lines older than VERI_LOAD_WINDOW (default 600) seconds do not count toward a load timeout ⟦criterion 2⟧
- [x] a lowering never writes a T below 2 ⟦criterion 4⟧
- [x] while the load file holds a whole number of at least 2, budget() returns max(2, min(T without it, that number)); anything else in it is ignored ⟦criterion 4⟧
- [x] a load timeout within VERI_LOAD_WINDOW seconds of the lowering on record (line 2) lowers nothing more ⟦criterion 5⟧
- [x] a lowering prints one stderr line naming the window's timed-out cases, the old T and the new, and records a `t-lowered` event (`old`, `new`, `cases`) ⟦criterion 7⟧
- [x] a timeouts or load file the plugin cannot read or write is one stderr line naming it, and the leg's exit code stays 1 for a timed-out case ⟦criterion 9⟧
- [ ] test-ceiling.sh's exit 0 removes VERI_TEST_LOAD_FILE; its exits 1 and 2 leave it ⟦criterion 6⟧
- [ ] dispatch.sh, at a poll finding a lowering on record newer than the last it reported, prints `t-lowered <old> <new> <cases>`, exits 0 and records the lowering's time in .tdd/dispatch-notified; a restarted dispatch.sh never prints it again ⟦criterion 8⟧
- [ ] only the leg, its plugin, veri/ceiling.py and veri/dispatch.py name VERI_TEST_LOAD_FILE ⟦criterion 10⟧
- [ ] vdev's Speaking sends the `t-lowered` closing line as a notice, then reruns dispatch.sh (graded) ⟦criterion 8⟧
- [ ] CLAUDE.md's Testing idiom states the load timeout and its lowering (graded) ⟦criterion 12⟧
- [ ] SCRIPTS.md's test-ceiling.sh and dispatch.sh entries name the load file removal and the `t-lowered` line (graded) ⟦criterion 13⟧

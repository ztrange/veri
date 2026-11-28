# Plan for #4843 — test_2717 and test_3375 stay green under the breaks #4816 named: the lock-wait pause and the group TERM are unguarded

- [x] test_2717 goes red on its own (code, acquired) assertion when supervise.py's lock-wait pause is removed, holding the lock by injected ticks instead of a real sleep ⟦criterion 1⟧
- [x] test_3375 goes red naming the group member's signal when stop_run.py sends TERM to the pid instead of its group ⟦criterion 2⟧
- [ ] no real wait grows and #4816's shrunk waits stay ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] test_supervise_process.py and test_stop_run_process.py pass ⟦full-suite⟧ ⟦criterion 4⟧

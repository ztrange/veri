# Plan for #3382 — restart-conductor.sh rewrites its at-ledger stop every 5 s and leaves .tdd/stop behind when the run ends without stopping

- [x] With growth over the threshold and a conductor that stays alive for several passes, restart_conductor.main calls stop_run once, not once per pass (in-process, fake conductor_alive, _growth, stop_run and sleep; small case, no process) ⟦criterion 1⟧
- [x] When the watcher has asked and the run's state at the conductor's exit is not stopped, the at-ledger .tdd/stop the watcher wrote is removed along with restart-pending (in-process, small case, no process) ⟦criterion 2⟧
- [x] A .tdd/stop the watcher did not write (one holding now, as stop-run.sh writes) is left in place by the watcher's not-stopped exit path (in-process, small case, no process) ⟦criterion 3⟧
- [ ] Guard: when the run reaches stopped after the watcher asked, the watcher still relaunches the conductor once and the restart is unchanged (in-process, small case, no process) ⟦criterion 4⟧
- [ ] Manual check: break the single-ask logic on purpose (ask every pass), see the single-ask case go red, restore ⟦human-owed⟧ ⟦criterion 4⟧

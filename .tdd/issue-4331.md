# Plan for #4331 — restart-conductor.sh relaunches a run whose conductor stopped on an operator's stop request, because run_state cannot tell it from its own growth stop

- [x] a stop request written over the restarter's own after it asked, then consumed by the conductor, ends the watch with `restarts 7 0`, exit 0, no relaunch and no `conductor-restart` event ⟦criterion 1⟧
- [x] a conductor that consumed only the restarter's own stop request (the stop file it wrote, then gone) is still relaunched once with a `conductor-restart` event ⟦criterion 2⟧
- [x] a stop request the restarter did not make, written after the conductor's last live poll and still in place when its exit is read, ends the watch with `restarts 7 0` and no relaunch ⟦criterion 1⟧

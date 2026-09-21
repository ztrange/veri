# Plan for #387 — stop-run.sh: the operator's stop command, and the TERM that `now` sends to the live leaf's supervisor

- [x] an unknown --mode value, both an issue and --all, neither, and a non-integer issue each exit 2, write no .tdd/stop and signal nothing ⟦criterion 9⟧
- [x] stop-run.sh --mode with no value following it prints a named complaint on stderr and exits 2, instead of dying on an unbound $2 with exit 1 ⟦added⟧ ⟦criterion 9⟧
- [x] stop-run.sh --mode now <n> writes `now` as the only line of that run's .tdd/stop, names the run on stdout and exits 0 ⟦criterion 1⟧
- [x] stop-run.sh <n> with no --mode writes at-ledger ⟦criterion 2⟧
- [x] a second call for the same run overwrites the mode already in .tdd/stop ⟦criterion 3⟧
- [x] stop-run.sh --all writes the mode into every live run's .tdd/stop and into no other ⟦criterion 4⟧
- [x] an issue with no worktree, an issue whose .tdd/conductor.pid names no live process, and --all with no live run each exit 3 and write no .tdd/stop ⟦criterion 5⟧
- [x] no main working tree to resolve exits 2 and writes nothing
- [x] stop-run.sh --mode now <n> sends TERM to the pid in <run>/.tdd/<name>.pid whose process runs `supervise.sh <name> `, and to no pid whose process is gone or runs something else ⟦criterion 6⟧ ⟂ refactor pending
- [ ] stop-run.sh --mode at-ledger <n> and --mode at-leaf <n> signal nothing ⟦criterion 7⟧
- [ ] stop-run.sh never signals the pid in .tdd/conductor.pid ⟦criterion 8⟧

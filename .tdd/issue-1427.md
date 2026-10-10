# Plan for #1427 — A leaf killed by pattern (pkill -f) despite the prompt rule from #1174/#1223; nothing enforces it

- [x] A leaf launched through run-leaf.sh has a `pkill` or `killall` command it issues refused before it runs: the command signals no process, and the refusal text names the rule — signal only processes you started, by the pid you recorded ⟦criterion 1⟧
- [x] A leaf launched through run-leaf.sh has a `kill $(pgrep …)` command it issues refused before it runs, with the refusal naming the same rule, while a `pgrep` that a script or suite the leaf runs calls internally (supervise.py's `pgrep -g`) still works ⟦criterion 1⟧
- [x] A leaf launched through run-leaf.sh can still `kill <pid>` a process it started itself and recorded the pid of: that command is not refused ⟦criterion 1⟧
- [ ] The refusal is watched red with the guard removed: the guard is taken out by hand, the pinning cases are seen to fail, and the guard is put back, with that record left on the PR ⟦human-owed⟧ ⟦criterion 2⟧

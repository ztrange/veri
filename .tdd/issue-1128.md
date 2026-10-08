# Plan for #1128 — orchestrate.sh relaunches without end a conductor that cannot start

- [x] when `run-conductor.sh` is missing, `orchestrate.sh` exits 2 with exactly one stderr line naming `run-conductor.sh` and the reason (No such file or directory), launching nothing further ⟦criterion 1⟧
- [x] when `run-conductor.sh` exists but is not executable (mode 644), `orchestrate.sh` exits 2 with exactly one stderr line naming `run-conductor.sh` and the reason (Permission denied), launching nothing further ⟦criterion 1⟧
- [x] after a failed conductor launch, `orchestrate.sh` asks `solvable-issues.sh` no further time — it was asked exactly once ⟦criterion 2⟧
- [ ] a conductor that starts and exits with its issue still listed and unparked is relaunched, and `solvable-issues.sh` is asked again, as today ⟦criterion 3⟧
- [ ] `orchestrate.sh`'s header `Exit:` line documents exit 2 for a `run-conductor.sh` that cannot be started ⟦diff-checked⟧

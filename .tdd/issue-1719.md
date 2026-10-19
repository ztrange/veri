# Plan for #1719 — PRD 011 helper: solvable-issues.sh --not-running omits issues whose conductor is already live

- [x] `solvable-issues.sh --not-running` omits an issue that has a live `run-conductor.sh <n>` process started from this clone's own skill scripts path (the directory holding the running `solvable-issues.sh`), and otherwise prints what `solvable-issues.sh` prints, in the same order; the process listing is faked at its process boundary in a small pytest case ⟦criterion 1⟧
- [x] Under `--not-running`, a live `run-conductor.sh <n>` process started from a different skill scripts path, such as a temporary copy of the skill, does not cause `<n>` to be omitted ⟦criterion 2⟧
- [x] Without `--not-running`, `solvable-issues.sh` prints the same numbers in the same order and exits the same code even while a live `run-conductor.sh <n>` from this clone's skill path is listed ⟦criterion 3⟧
- [x] Under `--not-running`, a conductor in the production process shape — the python interpreter running `<this clone's scripts>/veri/run_conductor.py <n>` — is recognised as live and `<n>` is omitted, pinned by a process listing of that real shape, not a hand-written `bash …/run-conductor.sh <n>` line ⟦criterion 4⟧ ⟂ refactor pending
- [ ] When `--not-running` filters out every solvable issue, `solvable-issues.sh` exits 3 with empty stdout ⟦criterion 5⟧
- [ ] `solvable-issues.sh --not-running --repo <x>` is accepted: it reads `<x>`'s issues and omits live conductors' issues ⟦criterion 6⟧
- [ ] `solvable-issues.sh --repo <x> --not-running` is accepted the same way, and the usage line `solvable-issues.sh` prints on a refused invocation, and its shim's usage comment, name only argument orders that parse ⟦criterion 6⟧

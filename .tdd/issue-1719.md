# Plan for #1719 — PRD 011 helper: solvable-issues.sh --not-running omits issues whose conductor is already live

- [ ] `solvable-issues.sh --not-running` omits every issue that has a live `run-conductor.sh <n>` process started from this clone's own skill path (the `run-conductor.sh` beside `solvable-issues.sh`), and otherwise prints what `solvable-issues.sh` prints, in the same order — a small in-process pytest case, the process listing faked at its one wrapper ⟦criterion 1⟧
- [ ] Under `solvable-issues.sh --not-running`, a live `run-conductor.sh <n>` started from a different skill path, such as a temporary copy of the skill, does not cause `<n>` to be omitted — a small in-process pytest case, the process listing faked at its one wrapper ⟦criterion 2⟧
- [ ] Without `--not-running`, `solvable-issues.sh`'s output is unchanged even while a live `run-conductor.sh <n>` from this clone's skill path runs — a small in-process pytest case, the process listing faked at its one wrapper ⟦criterion 3⟧
- [ ] The `solvable-issues.sh` entry in `SCRIPTS.md` and the shim's `Usage:` header name `--not-running` and what it omits ⟦diff-checked⟧

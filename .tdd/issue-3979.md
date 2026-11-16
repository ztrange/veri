# Plan for #3979 — PRD 021.3: a merge that landed is reported as landed

- [x] a merge call that exits 0, a read with no answer, then a read of `merged: true` ends with exit 0, the tag cut and the cleanup done ⟦criterion 1⟧
- [x] a merge call that exits 0 followed by a window in which no read answered releases the lock and exits 2, saying the merge call succeeded and the PR's state could not be read ⟦criterion 2⟧
- [ ] a merge call that exits 0 followed by reads that answer and never say merged exits 1, the lock released ⟦criterion 3⟧
- [ ] a merge call that exits non-zero followed by a window in which no read answered exits 2, the lock released once ⟦criterion 4⟧
- [ ] a merge call that exits non-zero followed by reads that answer and never say merged exits with the call's own code, the lock released once ⟦criterion 5⟧
- [ ] the `queued-merge.sh` entry of `skills/tdd/SCRIPTS.md` states the window after either kind of merge call and its exits ⟦criterion 6⟧

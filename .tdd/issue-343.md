# Plan for #343 — status.sh and the dashboard report every committed ledger in a run worktree as a run of its own

- [x] status.sh prints exactly one run for a run directory, identified by that directory's own issue number, ignoring other issues' committed ledgers ⟦criterion 1⟧
- [x] With two run directories each also holding the other's committed ledger, status.sh --json prints exactly two objects, each carrying only its own directory's events totals ⟦criterion 2⟧
- [ ] A run directory holding no ledger for its own issue number contributes no run and does not make status.sh exit non-zero ⟦criterion 3⟧
- [ ] /api/metrics keys exactly one entry per run directory by that directory's issue number, and runs metrics.sh at most once per live run directory ⟦criterion 4⟧
- [ ] /api/events answers by the run directory's own issue number, so an issue present only as a committed ledger copy inside another run returns the empty list ⟦criterion 5⟧

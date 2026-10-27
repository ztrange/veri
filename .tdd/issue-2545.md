# Plan for #2545 — status.sh and watch-runs.sh survive a run's worktree being removed mid-read

- [ ] status.sh --json reports a run whose events.jsonl or ledger vanishes between the existence check and the read as absent, not a crash: exit 0 (or 3 when no run is left), no traceback; pinned by a case that removes the file between the check and the read ⟦criterion 1⟧
- [ ] watch-runs.sh keeps watching when a run's worktree is removed mid-read: a removed run that was not among the conductors live at start produces no line and no exit; pinned by a case ⟦criterion 2⟧

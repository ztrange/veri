# Plan for #2871 — queued-merge.sh run from the worktree it merges orphans the merge lock and leaves main unforwarded

- [x] When queued-merge.sh runs from a copy of the scripts inside the linked worktree it merges and removes, with that worktree as its working directory too, the merge lock in the primary clone is free afterwards (a process case with a real linked worktree, gh and remote git faked on PATH) ⟦criterion 1⟧ ⟂ refactor pending
- [ ] In that same kind of run, main in the primary clone is fast-forwarded to origin/main and queued-merge.sh exits 0 (a process case with a real linked worktree, gh and remote git faked on PATH) ⟦criterion 2⟧
- [ ] When the merge lock cannot be released during cleanup because merge-lock.sh cannot be started, queued-merge.sh prints its "merged, but cleanup failed: release" line and exits 2 rather than dying on a traceback

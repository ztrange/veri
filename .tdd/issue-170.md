# Plan for #170 — solvable-issues.sh lists an issue whose conductor is running but has not opened its PR yet

- [x] solvable-issues.sh excludes an issue whose worktree holds a live conductor PID, and still lists one with no worktree or a dead PID
- [x] A bailed or killed run's issue (dead PID, no open PR) is printed by solvable-issues.sh so a resume is still possible
- [x] issue-worktree.sh idempotent path exits 2 naming the holder when a live conductor PID is found, instead of handing the path back
- [x] CONTEXT.md Solvable entry names the conductor PID lock as the in-flight signal

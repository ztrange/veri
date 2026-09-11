# Plan for #43 — Issue branch lives in its own git worktree, never in the caller's checkout

- [x] a fresh call creates a worktree at .tdd/wt/<n> on a new branch tdd/<n>-<slug> off the default branch and prints its path
- [x] a second call for the same issue prints the same path, exits 0, and creates nothing new
- [x] when the branch is already checked out in another worktree, it exits 2 naming that path and touches nothing
- [x] --remove <n> removes a clean worktree and refuses one with uncommitted changes with exit 2
- [x] when the branch already exists but no worktree holds it, the call checks it out into .tdd/wt/<n> instead of failing on -b

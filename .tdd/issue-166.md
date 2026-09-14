# Plan for #166 — issue-worktree.sh nests the issue worktree inside whichever linked worktree it runs from

- [x] Run from inside a linked worktree, `issue-worktree.sh <n> <slug>` creates and prints `<main-working-tree>/.tdd/wt/<n>`, not a path inside the linked worktree
- [ ] A later call for the same issue from the main working tree prints the same path and creates nothing
- [ ] `issue-worktree.sh --remove <n>` run from a linked worktree removes the worktree under the main working tree
- [ ] The path printed is the symlink-resolved one git itself reports, so it matches the `worktree` line `git worktree list --porcelain` prints for it even when the repo is reached through a symlinked path

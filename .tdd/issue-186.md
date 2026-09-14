# Plan for #186 — issue-worktree.sh re-cuts a branch that exists only on the remote, abandoning a pushed run

- [x] A branch that exists only as refs/remotes/origin/<name> is checked out at its own tip, with its commits and committed ledger present in the new worktree
- [x] That worktree's branch tracks the remote branch so git status and push address the right upstream
- [ ] A branch that exists locally and is ahead of its remote is checked out without being rewound to the remote tip
- [ ] A name that exists neither locally nor on any remote is still cut from the default branch

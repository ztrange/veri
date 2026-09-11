# Plan for #65 — Test the default-branch resolution and no-default exit 2 path of issue-worktree.sh

- [ ] a clone whose `origin/HEAD` points at a branch named neither `main` nor `master`, with no local branch of either name, cuts the new worktree from that remote branch — exit 0, tip equal to it
- [ ] a repo with no remote and only a local `master` cuts the new branch from `master` — exit 0
- [ ] a repo with no remote and no `main`/`master` exits 2 with a diagnostic on stderr, nothing on stdout, and git's worktree and branch registry unchanged

# Plan for #174 — issue-worktree.sh cuts the issue branch from the local main, which lags origin while runs are live

- [x] In a repository whose `origin` default branch is ahead of the local one, `issue-worktree.sh <n> <slug>` creates the issue branch at `origin`'s tip
- [x] Creating the issue branch leaves the local default branch ref and the main working tree unchanged
- [x] The newly created issue branch has no upstream
- [x] When the fetch fails, the script exits 2 with a diagnostic on stderr and creates no worktree and no branch
- [x] A repository with no remote still cuts the issue branch from its local `main`/`master`
- [x] A resume onto an existing issue branch checks it out as it is and attempts no fetch
- [x] `SKILL.md`'s description of `issue-worktree.sh` says the branch is cut from the freshly fetched remote default branch, and why the local one is not used
- [x] A clone that has an `origin` remote but no `refs/remotes/origin/HEAD` still cuts the issue branch from the remote's freshly fetched tip (plan amendment)

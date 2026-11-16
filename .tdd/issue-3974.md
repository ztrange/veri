# Plan for #3974 — PRD 022.15: a run is refused as claimed only by a PR in this repository

- [ ] `issue_worktree.claiming_pr` returns only a PR whose head is in this repository, requesting `isCrossRepository`: a fork PR saying `Closes #7` lets `issue-worktree.sh 7 <slug>` proceed, a same-repository one still refuses ⟦criterion 1⟧
- [ ] the PR-claim ratchet no longer exempts `issue_worktree`
- [ ] the `issue-worktree.sh` entry of SCRIPTS.md says only a PR whose head is in this repository claims the issue ⟦criterion 2⟧

# Plan for #4080 — PRD 013.19: take over a run from another machine in one command

- [ ] `issue-worktree.sh --take-over <n> <slug>` creates the worktree on a local branch cut from `origin/<branch>` where without the flag it refuses with "another run holds it" ⟦criterion 1⟧
- [ ] without `--take-over`, `issue-worktree.sh` still refuses in that case, exit 2, adding no worktree, and its refusal names `--take-over` as the way to take the run over ⟦criterion 2⟧

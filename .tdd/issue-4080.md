# Plan for #4080 — PRD 013.19: take over a run from another machine in one command

- [x] `issue-worktree.sh --take-over <n> <slug>` creates the worktree on a local branch cut from `origin/<branch>` where without the flag it refuses with "another run holds it" ⟦criterion 1⟧
- [x] without `--take-over`, `issue-worktree.sh` still refuses in that case, exit 2, adding no worktree, and its refusal names `--take-over` as the way to take the run over ⟦criterion 2⟧
- [x] `--take-over` fetches the run's branch from origin before cutting the worktree, so it cuts from origin's current tip, and exits 2 naming the fetch when it gets no answer ⟦criterion 1⟧
- [ ] `--take-over` asks origin for the run's branch when no remote-tracking ref names it, then fetches and cuts ⟦criterion 1⟧
- [ ] `--take-over` over a local branch that differs from origin's after the fetch exits 2 naming both shas and what to do ⟦criterion 1⟧

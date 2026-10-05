# Plan for #819 — live_conductor, rebase-onto-default and issue-worktree act only on what the run owns

- [x] issue-worktree.sh hands back an existing registered worktree whose .tdd/conductor.pid holds 0 or 00, printing its path and exiting 0, rather than refusing it as held by a live conductor ⟦criterion 1⟧
- [ ] stop-run.sh for an issue whose worktree's .tdd/conductor.pid holds 0 or 00 exits 3 and writes no .tdd/stop request ⟦criterion 1⟧
- [ ] rebase-onto-default.sh run while a rebase is already in progress in the worktree exits 2 and leaves that rebase in progress, with HEAD and the rebase state directory unchanged ⟦criterion 2⟧
- [ ] issue-worktree.sh <n> <slug> given an <n> that is not a positive whole number exits 2 with its usage on stderr and creates no worktree and no branch ⟦criterion 3⟧
- [ ] issue-worktree.sh --remove <n> given an <n> that is not a positive whole number exits 2 with its usage on stderr and removes no worktree ⟦criterion 3⟧
- [ ] every case each script's suites already hold passes with its assertions unchanged, apart from an assertion pinning a defect fixed above, listed by file:line in the PR body ⟦full-suite⟧ ⟦criterion 4⟧

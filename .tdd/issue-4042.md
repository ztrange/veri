# Plan for #4042 — PRD 025.14: the default branch is read in one place

- [ ] issue_worktree.default_branch_name reads the branch through git.default_branch and returns the same (name, message) pair with origin/HEAD set, unset with an origin naming a branch, unset with an origin naming none, and no origin with a local main, master or neither ⟦criterion 1⟧
- [ ] ready_check.default_tip reads the branch through git.default_branch(remote=False): ready-check.sh reads the workflows at origin's default tip with origin/HEAD set, and at main unset ⟦criterion 2⟧
- [ ] update_veri.py reads the branch through git.default_branch(cwd=<its clone>, remote=False), its refusals' text and exit codes unchanged, origin/HEAD unset included ⟦criterion 3⟧ ⟦criterion 4⟧

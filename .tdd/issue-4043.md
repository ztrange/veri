# Plan for #4043 — PRD 025.15: no module has its own git exception

- [ ] diff_leaf_deviation.py runs git through git.out and catches git.GitFailed, with no _git and no GitFailure; a failing git call still prints `diff-leaf-deviation.sh: git <args> failed: <stderr>` and exits 2; it leaves MODULES_RUNNING_GIT_DIRECTLY ⟦criterion 1⟧ ⟦criterion 3⟧ ⟦criterion 4⟧
- [ ] resume_clean.py runs git through veri/git.py and catches git.GitFailed, with no git helper and no GitFailed class of its own; resume-clean.sh's stdout, stderr and exit code are unchanged on a failing reset with saved appends and without; it leaves MODULES_RUNNING_GIT_DIRECTLY ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 4⟧

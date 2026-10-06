# Plan for #1033 — preserve-attempt.sh drops a tracked file that .gitignore matches from the preserved attempt

- [x] A file tracked in HEAD and matched by .gitignore appears in the preserved attempt's tree with its worktree content, the in-process cases that pin the snapshot's git call sequence updated to the new sequence ⟦criterion 1⟧
- [x] Beside a tracked file .gitignore matches, an untracked ignored file is absent from the preserved tree, an untracked non-ignored file is present, and a tracked file deleted from the worktree is absent ⟦criterion 2⟧
- [x] Preserving a worktree holding a tracked file .gitignore matches leaves the caller's index, HEAD and branch untouched ⟦criterion 3⟧
- [x] The existing contract cases in tests/preserve-attempt.test.sh are unchanged by the branch, tests/py/test_preserve_attempt.py changes only assertions pinning the snapshot's git call sequence, and both suites are green ⟦diff-checked⟧ ⟦criterion 4⟧
- [x] make test is green ⟦full-suite⟧ ⟦criterion 5⟧

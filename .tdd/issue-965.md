# Plan for #965 — issue-worktree.sh exits 1 with a traceback on a non-UTF-8 or unreadable conductor.pid

- [x] through the issue-worktree.sh entry point (tests/issue-worktree.test.sh), a second call for a registered worktree whose .tdd/conductor.pid holds the bytes \xff\xfe\n prints the worktree's path on stdout, exits 0 and prints nothing on stderr ⟦criterion 1⟧
- [x] in tests/py/test_issue_worktree.py, main for a registered worktree whose pid file open cannot read (open faked to raise PermissionError for that one path, never permission bits) returns 0 and writes the path, with no exception ⟦criterion 2⟧ ⟂ refactor pending
- [ ] the existing pid-file cases in tests/py/test_issue_worktree.py (digits answered as read; 0 and 00 not live, #819) and tests/issue-worktree.test.sh pass with their assertions unmodified by this branch ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] no bash file changes on this branch: lib/number-in.sh and lib/pid-file.sh stay byte-identical, and issue-worktree.sh stays the shim ⟦diff-checked⟧ ⟦criterion 4⟧

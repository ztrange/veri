# Plan for #2784 — A verifier leaf refused for an unreadable file leaves the files it added

- [ ] After a refusal for an unreadable file left by a verifier leaf, a new file the leaf added no longer exists in the worktree and the exit is still 2: a process case in `skills/tdd/scripts/tests/py/test_verify.py` with a stub `CLAUDE_BIN` in a real git scratch repository, failing on the current code ⟦criterion 1⟧
- [ ] After the same refusal, an untracked file that existed before the leaf launched is still there with its contents unchanged: a process case in `skills/tdd/scripts/tests/py/test_verify.py` with a stub `CLAUDE_BIN` in a real git scratch repository ⟦criterion 2⟧

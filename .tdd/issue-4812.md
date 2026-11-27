# Plan for #4812 — perf: event and detect_test_command import github, git and tempfile only on the path that needs them

- [ ] `event` imports `github` only on the path that needs it: the guard's `RARE_PATH_IMPORTS` row `"event": {"github": …}` passes and fails with the import back at module level ⟦criterion 1⟧
- [ ] `detect_test_command` imports `git` and `tempfile` only on the `--at` path: the guard's row `"detect_test_command": {"git": …, "tempfile": …}` passes and fails with either import back at module level ⟦criterion 2⟧

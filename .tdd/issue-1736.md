# Plan for #1736 — wrong-test-route: skip .git, .tdd, .venv and node_modules, and read only WRONG_TEST: lines, each pinned

- [ ] wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `.git/`, pinned by a case that goes red when the `.git` skip is removed ⟦criterion 1⟧
- [ ] wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `.tdd/wt/<n>/` (another run's worktree), pinned by a case that goes red when the `.tdd` skip is removed ⟦criterion 1⟧
- [ ] wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `.venv/` ⟦criterion 1⟧
- [ ] wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `node_modules/` ⟦criterion 1⟧
- [ ] wrong-test-route answers exit 3 `revise` when a green report names a real case of the repo's own tests only on lines other than `WRONG_TEST:`, pinned by a case that goes red when the `WRONG_TEST:` line filter is removed ⟦criterion 2⟧

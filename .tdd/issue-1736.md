# Plan for #1736 — wrong-test-route: skip .git, .tdd, .venv and node_modules, and read only WRONG_TEST: lines, each pinned

- [x] wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `.git/` (already satisfied by the existing skip: a regression pin, test only, no production change) ⟦criterion 1⟧
- [x] wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `.tdd/wt/<n>/`, another run's worktree (already satisfied by the existing skip: a regression pin, test only, no production change) ⟦criterion 1⟧
- [x] wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `.venv/` ⟦criterion 1⟧
- [x] wrong-test-route answers exit 3 `revise` when the case a `WRONG_TEST:` line names exists only in a test file under `node_modules/` ⟦criterion 1⟧ ⟂ refactor pending
- [ ] wrong-test-route answers exit 3 `revise` when a green report names a real case of the repo's own tests only on lines other than `WRONG_TEST:` (already satisfied by the existing line filter: a regression pin, test only, no production change) ⟦criterion 2⟧

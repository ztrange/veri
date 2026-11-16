# Plan for #3952 — PRD 017.10: rerecord-rebased takes the default branch from case_history

- [x] `case_history` answers the default branch (raising `GitFailed` when there is none), `rerecord-rebased` takes it from there, and `tests_frozen.py` imports and calls nothing of `git`; `rerecord-rebased` still exits 2 with no `refs/remotes/origin/HEAD` ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 3⟧
- [x] `tests-frozen.sh rerecord-rebased` in a repository with no `refs/remotes/origin/HEAD` exits 2 and its stderr names that ref, pinned by one new case ⟦criterion 2⟧

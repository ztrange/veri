# Plan for #1748 — run-finished.sh: an empty PR URL reads the current branch's PR; indented checkboxes and a missing ledger

- [x] When a done run's recorded PR URL is empty, run-finished.sh exits 2 with one stderr line saying no PR is recorded, and never calls `gh pr view` without a URL — even when run from a worktree whose branch has an open PR (pinned by a case with gh faked, the fake answering a URL-less `gh pr view` with an open PR's body) ⟦criterion 1⟧
- [x] An indented unticked human-owed checkbox in the PR body (`  - [ ] … ⟦human-owed⟧`) counts as unmet exactly as one at the start of the line does: exit 1, its `human-owed` line printed (pinned by a case with gh faked) ⟦criterion 2⟧
- [x] An unticked human-owed checkbox in the PR body written `* [ ] … ⟦human-owed⟧` counts as unmet exactly as `- [ ]` does: exit 1, its `human-owed` line printed (pinned by a case with gh faked) ⟦criterion 2⟧ ⟂ refactor pending
- [ ] When a done run's ledger `issue-<n>.md` is missing, run-finished.sh exits 2 with one stderr line naming the missing file and no Python traceback (pinned by a case) ⟦criterion 2⟧
- [ ] A run whose state is `stale` is reported not done: exit 1 and the state `stale` named on stdout, exactly as a bailed or stopped run is (pinned by a case, so a check written as `state in ("bailed", "stopped")` goes red) ⟦criterion 3⟧
- [ ] A run whose state is `running` is reported not done: exit 1 and the state `running` named on stdout, exactly as a bailed or stopped run is (pinned by a case, so a check written as `state in ("bailed", "stopped")` goes red) ⟦criterion 3⟧
- [ ] run-finished.test.sh's first case builds its scratch repo with the harness's `new_repo` instead of a bare `git init`; no production change and no change to what the case asserts ⟦diff-checked⟧

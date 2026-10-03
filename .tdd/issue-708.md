# Plan for #708 — test_status.py has one fake_git (with a linked-worktree option) and one ledger writer

- [x] fake_git takes an optional linked worktree, answering `git worktree list` with the main tree then that linked one, and the main-working-tree case uses it in place of its own fake_run, setattr and delenv, leaving test_status.py with one fake for subprocess.run ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] one helper taking the issue number and the ledger text makes `.tdd/wt/<issue>/.tdd/issue-<n>.md`, and every case that needs a run directory with a ledger gets it from that helper rather than its own mkdir(parents=True) and write_text ⟦diff-checked⟧ ⟦criterion 2⟧
- [x] every case in test_status.py keeps its name and its assertions, and a command the fake does not expect still raises `unexpected command: …` ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] the fake's `unexpected command: …` failure was broken on purpose and seen red, then restored ⟦human-owed⟧ ⟦criterion 3⟧
- [x] `make test` is green ⟦full-suite⟧ ⟦criterion 4⟧

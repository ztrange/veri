# Plan for #1528 — event.py writes .tdd/events.jsonl under the caller's cwd

- [x] An event recorded with the default directory from a directory outside any git worktree still lands in ./.tdd/events.jsonl under that directory ⟦criterion 2⟧
- [x] An explicit non-empty directory argument to event.append and event.mark is used as given, even when cwd is a subdirectory of a git worktree ⟦criterion 2⟧
- [ ] An event recorded through event.sh with the default directory, with cwd set to a subdirectory of a temp git repo, lands in <repo toplevel>/.tdd/events.jsonl and no <subdir>/.tdd is created ⟦criterion 1⟧
- [ ] timed-test-run.sh's test-run event, run with cwd set to a subdirectory of a temp git repo, lands in <repo toplevel>/.tdd/events.jsonl and no <subdir>/.tdd is created ⟦criterion 1⟧

### in a linked worktree, whose .git is a file pointing at the common dir, the journal path's owner and repo are read from the common dir's config, by a small case with no git process ⟦criterion 1⟧
- test-only | `test_event_journal.py` builds a clone with a `.git/config` inline in six cases. One `clone_with` helper (or fixture) would replace those copies.
- test-only | The two cases that set `VERI_HOME` by hand with try/finally could take `monkeypatch.setenv`, as the defaults case already does.

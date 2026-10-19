# Plan for #1819 — handoff-state.sh raises IndexError in a repository with no tags

- [ ] A medium case (`@pytest.mark.process("git")`, real git) builds a scratch git repository with a `main` branch and no tags, runs handoff_state in it through `run_cli`, and gets exit 0, a first line `main <sha> (none)` naming main's sha and `(none)` for the missing tag, and no traceback on stderr ⟦criterion 2⟧
- [ ] When `git tag` lists no tags, handoff_state's first line is `main <sha> (none)` with exit 0 and no traceback, pinned by a small in-process case faking git ⟦criterion 1⟧

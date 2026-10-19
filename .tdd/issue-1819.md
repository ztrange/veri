# Plan for #1819 — handoff-state.sh raises IndexError in a repository with no tags

- [x] A medium case (`@pytest.mark.process("git")`, real git) builds a scratch git repository with a `main` branch and no tags, runs handoff_state in it through `run_cli` with `gh` faked the way test_handoff_state.py's cases do, by monkeypatching `handoff_state.open_prs` to return `[]` and `status.json_document` to return `(0, '{"runs": []}')`, so no network is reached, and gets exit 0, a first line `main <sha> (none)` naming main's sha and `(none)` for the missing tag, and no traceback on stderr ⟦criterion 2⟧
- [ ] When `git tag` lists no tags, handoff_state's first line is `main <sha> (none)` with exit 0 and no traceback, pinned by a small in-process case faking git ⟦criterion 1⟧

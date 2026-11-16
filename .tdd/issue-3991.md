# Plan for #3991 — PRD 021.17: a posted `✅ Done` is seen under every gh driver

- [x] `github.gh_json_page("", path)` with no gh arguments reads `path` through `gh api` under `VERI_GH_DRIVER` `rest`, `graphql` and `auto`, never running bare `gh`; a small case per driver in `tests/py/unit/test_github.py` asserting the argv ⟦criterion 1⟧
- [x] `run-conductor.sh`, after a conductor that exits 0 with no run-end mark, finds a `### ✅ Done` comment posted since the last resume under `VERI_GH_DRIVER` `graphql` and `auto` (bare `gh` answering its help text) and writes no `needs-user` bail; a process case per driver in `tests/py/test_run_conductor_process.py` ⟦criterion 2⟧
- [ ] the `gh_json_page(...)` entry of `skills/tdd/scripts/veri/README.md` says a call with no gh arguments is a REST read under every driver ⟦criterion 3⟧

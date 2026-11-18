# Plan for #4335 — A project-owned quiet test command keeps raw test output out of leaves

- [x] `detect-test-command.sh --tier "quiet test files"` prints the command of the repo's `CLAUDE.md` line `veri: quiet test files: <command>` ⟦criterion 1⟧
- [x] With no `veri: quiet test files:` line, `detect-test-command.sh --tier "quiet test files"` proposes `pytest -q --no-header -rf` for a repo whose pytest configuration it recognises ⟦criterion 1⟧
- [x] With no `veri: quiet test files:` line, `detect-test-command.sh --tier "quiet test files"` proposes `npx jest --silent` for a repo whose `package.json` test script runs jest ⟦criterion 1⟧
- [x] `detect-test-command.sh --tier "quiet test files"` exits 3, printing nothing, for a repo whose runner it cannot recognise (a `Makefile`, `npm test` or `go test` repo declaring no quiet line) ⟦criterion 1⟧
- [x] `detect-test-command.sh --tier "quiet test files" --issue <body>` never answers with the issue's `Test command:` line ⟦criterion 1⟧
- [x] `record-test-commands.sh --quiet '<cmd>' <fast> <all>` writes the `veri: quiet test files: <cmd>` line to `CLAUDE.md` where it stands, else appended, and an empty `--quiet` is refused with exit 2 ⟦criterion 1⟧
- [x] In a foreign tree whose `CLAUDE.md` declares `veri: quiet test files: <cmd>`, every leaf prompt that times a changed run gives `<cmd>` run over the changed files' tests as that run's command ⟦criterion 1⟧ ⟦criterion 2⟧
- [x] `timed-test-run.sh` running the declared quiet command hands its output to the caller unchanged and returns its exit status ⟦criterion 1⟧
- [ ] `timed-test-run.sh` reports a quiet command's exit 2 as a broken run, never as a test failure ⟦criterion 1⟧
- [ ] Outside veri's own tree, a `changed` run that is not the declared quiet command prints only the exit code, at most the output's last 20 lines and the saved file's path, the whole output saved under `.tdd/test-runs/` ⟦criterion 1⟧ ⟦criterion 2⟧
- [ ] `/vinstall`'s `## Recording the test commands`, the prompt fragment `_timed-test-run.md`, root `CLAUDE.md` (its `veri: quiet test files:` line and Testing idiom) and `skills/tdd/SCRIPTS.md` state the quiet command and the 20-line fallback; their requirement rows amended and regraded

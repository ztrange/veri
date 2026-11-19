# Plan for #4444 — A structural transform's verifier runs the fast tier plus the changed run

- [x] `build-verify-prompt.sh transform` without `--fast-cmd` exits 2 with `transform needs --fast-cmd '<fast-tier test command>'` ⟦criterion 1⟧ ⟦criterion 2⟧
- [x] the `transform` verifier prompt has it run the fast tier (`timed-test-run.sh fast '' <fast-cmd>`) before the `changed` run, both green ⟦criterion 1⟧
- [ ] `STRUCTURAL.md`'s `verdict-transform` launch passes `--fast-cmd '<fast-cmd>'` to `run-verdict.sh`, pinned by a case that goes red without it ⟦criterion 1⟧ ⟦criterion 2⟧

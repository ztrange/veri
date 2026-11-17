# Plan for #4122 — PRD 032.7: a run runs the repo's declared lint command once before readying

- [x] `detect-test-command.sh --tier lint` prints the command of the CLAUDE.md `veri: lint: <command>` line and exits 0 ⟦criterion 1⟧
- [x] `detect-test-command.sh --tier lint` with no such line exits 3 printing nothing, even with other `veri:` lines, a `Makefile` or an issue body's `Test command:` ⟦criterion 2⟧
- [ ] `detect-test-command.sh`'s usage line lists the `lint` tier ⟦criterion 3⟧
- [ ] `event.sh lint exit=<code>` is a declared event, with its `JOURNAL.md` row held by the journal roster cases ⟦criterion 4⟧
- [ ] `DRAFT-PR.md` runs the declared lint command before `refactor-candidates.sh`, writes the `lint` event and the PR body's `### Lint` section, and neither bails nor holds the PR on a non-zero exit ⟦criterion 5⟧
- [ ] `SCRIPTS.md`'s `detect-test-command.sh` entry names the `lint` tier ⟦criterion 6⟧

# Plan for #416 — affected-suites.sh widens on every green commit's run state

- [x] A range of a `.tdd/` ledger file plus one source change answers only that source change's suites, placing the run state as affecting none ⟦criterion 1⟧
- [x] A range whose files are all `.tdd/` run state exits 3 — nothing to do — rather than printing an empty answer ⟦criterion 2⟧
- [x] An unplaced path that is not `.tdd/` run state still widens the answer to every suite ⟦criterion 3⟧
- [x] The widening stderr line still names every unplaced file that caused it ⟦criterion 4⟧
- [x] A green-commit-shaped range — ledger, refactor-owed file and a real source change together — answers narrowly, pinning the regression ⟦criterion 5⟧
- [x] A range that adds or deletes a file under `tests/` or `tests/unit/` includes `claude-md-counts.test.sh` in the affected set ⟦criterion 6⟧
- [x] Editing an existing suite's contents does not include `claude-md-counts.test.sh` ⟦criterion 7⟧
- [x] A range that adds or deletes a script under `scripts/` also includes `claude-md-counts.test.sh`, since CLAUDE.md hand-types the script count beside the suite count ⟂ refactor pending

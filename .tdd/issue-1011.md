# Plan for #1011 — affected-suites.sh names a non-existent run-suite.test.sh for a change to run-suite.sh

- [x] For a range changing a script under skills/tdd/scripts/ with no same-named suite, affected-suites.sh prints no path that does not exist on disk ⟦criterion 1⟧
- [ ] For a range changing a script under skills/tdd/scripts/ with no same-named suite, affected-suites.sh prints the existing suites under skills/tdd/scripts/tests/ that name that script's file, so a change to run-suite.sh prints run-suite-venv.test.sh

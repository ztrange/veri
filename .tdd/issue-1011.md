# Plan for #1011 — affected-suites.sh names a non-existent run-suite.test.sh for a change to run-suite.sh

- [x] For a range changing a script under skills/tdd/scripts/ with no same-named suite, affected-suites.sh prints no path that does not exist on disk ⟦criterion 1⟧
- [x] For a range changing a script under skills/tdd/scripts/ with no same-named suite, affected-suites.sh prints the existing suites under skills/tdd/scripts/tests/ that name that script's file, so a change to run-suite.sh prints run-suite-venv.test.sh
- [ ] fix the full-suite failure: no-nested-suites.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ (or its unit/ tier) launches another real suite outside the exemptions recorded here (affected-suites.test.sh:162 and :179 name run-suite-venv.test.sh in a shape it treats as launching it) ⟦suite-repair⟧

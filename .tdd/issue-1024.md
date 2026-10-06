# Plan for #1024 — affected-suites.sh misses tests/unit suites that name a changed prompt or fixture

- [x] A change to a prompt under skills/tdd/scripts/prompts/ that a suite under tests/unit/ names prints that unit suite ⟦criterion 1⟧
- [x] A change to a fixture under skills/tdd/scripts/tests/fixtures/ that only a suite under tests/unit/ names prints that unit suite
- [x] A change to skills/tdd/scripts/<name>.sh with no suite of its own, named only by a suite under tests/unit/, prints that unit suite ⟦criterion 2⟧
- [x] A change to any skills/tdd/scripts/prompts/*.md, even one no suite names, prints skills/tdd/scripts/tests/unit/emitted-text.test.sh ⟦criterion 3⟧
- [x] A change to skills/tdd/scripts/<name>.sh with no suite of its own does not print a suite whose only mention of it is lib/<name>.sh ⟦criterion 4⟧
- [x] Existing cases in affected-suites.test.sh and test_affected_suites.py still pass ⟦full-suite⟧ ⟦criterion 5⟧

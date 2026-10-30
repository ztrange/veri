# Plan for #2673 — A re-record of a step's frozen record captures every case the step owns at HEAD, renamed successors and later pins included

- [x] After a step's case is renamed in a later commit, `tests-frozen.sh record --step <step> <file>` on HEAD records the renamed successor: pinned by a case in `skills/tdd/scripts/tests/py/unit/test_tests_frozen.py` whose fixture's record held 3 cases and whose file holds 4 ⟦criterion 1⟧
- [x] After a pin case is added for a step in a later commit, `tests-frozen.sh record --step <step> <file>` on HEAD records that later pin case: pinned by a case in `skills/tdd/scripts/tests/py/unit/test_tests_frozen.py` ⟦criterion 1⟧
- [ ] A case dropped from a re-record is dropped only because it no longer exists at HEAD, never because it is absent from the step's own commit: pinned by a case in `skills/tdd/scripts/tests/py/unit/test_tests_frozen.py` ⟦criterion 2⟧

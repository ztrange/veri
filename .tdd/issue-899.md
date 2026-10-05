# Plan for #899 — a nested make unit UNIT_TESTS=<fixture> still runs the full pytest leg, so one red pytest case also fails unit-tier.test.sh

- [x] make unit UNIT_TESTS naming one shell suite runs that suite and starts no pytest case, and exits 0 for a passing suite even while a pytest case elsewhere under tests/py is red ⟦criterion 1⟧
- [x] make unit UNIT_TESTS naming a set that includes a tests/py test_*.py file runs the pytest leg over that file only, not every test_*.py under tests/py ⟂ refactor pending
- [ ] a plain make unit, with no UNIT_TESTS on the command line, still runs every suite under tests/unit and the full pytest leg, and exits non-zero when a pytest case under tests/py fails ⟦criterion 2⟧
- [ ] unit-tier.test.sh passes under the repository's full test command, every one of its nested make unit calls naming UNIT_TESTS so none runs the pytest leg ⟦full-suite⟧ ⟦criterion 3⟧

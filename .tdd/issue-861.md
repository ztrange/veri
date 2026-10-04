# Plan for #861 — a nested make test TESTS=<fixture> still runs the full pytest leg, so one red pytest case fails five suites

- [x] `make test TESTS=<one shell suite>` runs that shell suite and no pytest case, so a red pytest case elsewhere under tests/py does not change its outcome ⟦criterion 1⟧
- [x] `make test TESTS=<a tests/py/test_*.py file>` runs that pytest file through the pytest leg, and only that file, rather than executing it as a shell suite
- [x] A plain `make test`, with no TESTS on the command line, still runs every shell suite and the full pytest leg, and fails when a pytest case fails ⟦criterion 2⟧
- [x] fix the full-suite failure: no-recipe-unit-tier.test.sh — FAIL - no suite under tests/ calls the test recipe with TESTS= and leaves UNIT_TESTS unemptied (pytest-leg.test.sh:393 and :408 call the recipe with TESTS= but no UNIT_TESTS=) ⟦suite-repair⟧ ⟦criterion 2⟧ ⟂ refactor pending
- [ ] The guard suites that nest `make test` (bash-version-guard, count-line-guard, make-test-env, unit-tier) still pass, with no FAIL caused by an unrelated red pytest case ⟦full-suite⟧ ⟦criterion 3⟧

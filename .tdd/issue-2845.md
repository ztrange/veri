# Plan for #2845 — wrong-test-route treats only an exact NONE as no missing test, so a verifier's `MISSING_TEST: none; …` reroutes to red-missing

- [x] A report with `MISSING_TEST: none; <text>` (lower case, trailing text) makes `wrong-test-route.sh` route exactly as the same report with `MISSING_TEST: NONE` does: it answers `revise`, never `missing`. A small in-process case in tests/py/unit/test_wrong_test_route.py ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `MISSING_TEST: None`, `MISSING_TEST: NONE.` and `MISSING_TEST: none - <text>` each route as `MISSING_TEST: NONE` does, answering `revise`. A small in-process case in tests/py/unit/test_wrong_test_route.py ⟦criterion 2⟧
- [ ] A report with `MISSING_TEST: nonexistent <behaviour>`, whose text merely begins with a longer word, still answers `missing nonexistent <behaviour>`. A small in-process case in tests/py/unit/test_wrong_test_route.py ⟦criterion 3⟧
- [ ] `wrong_test_route._missing`'s none test, broken on purpose back to exact `NONE`, turns the first criterion's case red, the record of that check being owed by a human ⟦human-owed⟧ ⟦criterion 4⟧

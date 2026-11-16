# Plan for #3946 — PRD 017.5: tests_frozen looks up case_history's toplevel and changed files when called

- [ ] `tests_frozen._toplevel` is a function of `tests_frozen.py` whose body calls `case_history.toplevel(`, so a fake of `case_history.toplevel` set after import reaches it ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 3⟧
- [ ] `tests_frozen.differing_tests` is a function of `tests_frozen.py` whose body calls `case_history.changed_test_files(`, so a fake of `case_history.changed_test_files` set after import reaches it ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 3⟧

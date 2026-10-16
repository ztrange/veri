### affected-suites.sh selects a changed `tests/py/unit/test_*.py` file as itself, exactly as it selects a changed `tests/py/test_*.py` file today; pinned by a case with a file in `tests/py/unit/` ⟦criterion 2⟧
- test-only | `test_affected_suites.py`: the two new cases (module mapping and changed-file selection) share their setup of mkdir, write and chdir, which a helper could remove

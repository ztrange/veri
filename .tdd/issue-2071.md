# Plan for #2071 — grade-prose.sh crashes on a non-integer or negative VERI_NO_VERDICT_RETRIES

- [x] grade-prose.sh run with a non-integer VERI_NO_VERDICT_RETRIES (e.g. abc), past its earlier checks, exits 2 with stderr naming VERI_NO_VERDICT_RETRIES and no Python traceback, launching no grader leaf (a small in-process case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py) ⟦criterion 1⟧
- [ ] grade-prose.sh run with a negative VERI_NO_VERDICT_RETRIES (e.g. -1), past its earlier checks, exits 2 with stderr naming VERI_NO_VERDICT_RETRIES and no Python traceback, launching no grader leaf (a small in-process case in skills/tdd/scripts/tests/py/unit/test_grade_prose.py) ⟦criterion 1⟧

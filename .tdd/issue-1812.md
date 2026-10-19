# Plan for #1812 — affected-suites: no case pins that an unhandled file widens to every suite but skips a suite-named directory

- [ ] A case in skills/tdd/scripts/tests/py/test_affected_suites.py changes a file no rule handles, such as docs/notes.md, and pins that affected-suites prints exactly the bash suite files every_suite() lists (skills/tdd/scripts/tests/*.test.sh and tests/unit/*.test.sh, no pytest modules) and leaves out a directory named like a suite; a small in-process case, no production change ⟦criterion 1⟧
- [ ] The case is watched to fail, with the widening or the directory skip reverted ⟦human-owed⟧ ⟦criterion 2⟧

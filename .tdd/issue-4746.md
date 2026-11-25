# Plan for #4746 — affected-suites.sh lists the pyflakes gate case when a change touches a .py file

- [x] in veri's own tree, a range changing a `veri/<m>.py` module also prints `skills/tdd/scripts/tests/py/test_ruff_tree_audit_process.py`, exit 0 ⟦criterion 1⟧
- [ ] in veri's own tree, a range changing a `tests/py/unit/test_<m>.py` file also prints the pyflakes gate case, exit 0 ⟦criterion 1⟧
- [ ] in veri's own tree, a range changing only a `.md` file does not print the pyflakes gate case ⟦criterion 2⟧
- [ ] in veri's own tree, a range changing only a `.sh` shim does not print the pyflakes gate case ⟦criterion 2⟧
- [ ] a foreign tree's range changing a `.py` file does not print the pyflakes gate case ⟦criterion 3⟧
- [ ] CLAUDE.md's Testing idiom paragraph on `affected-suites.sh` states the pyflakes gate rule, regraded ⟦criterion 5⟧
- [ ] SCRIPTS.md's `affected-suites.sh` entry states the pyflakes gate rule, regraded ⟦criterion 6⟧

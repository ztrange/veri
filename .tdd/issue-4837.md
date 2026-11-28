# Plan for #4837 — refactor: the repo prose-audit cases drop their redundant whole-repo prose-owed run and move to the fast tier

- [x] coverage holds before the move: a `skills/tdd/GRADED` line removed, a prompts `REQUIREMENTS.md` heading renamed, and row PL64 moved off its unit each turn the old process file red, then green restored ⟦criterion 4⟧
- [x] the 13 kept cases read `GRADED` and `REQUIREMENTS.md` directly in `tests/py/unit/test_prose_units_signed.py`, with no prose-owed run and no `process` or `tree_audit` mark ⟦criterion 3⟧
- [x] `test_2307` and `test_prose_owed_repo_audit_process.py` are deleted, and `specs/prd-024.md` MV8 names the new file ⟦criterion 2⟧
- [x] no case under `tests/py/` runs `prose-owed.sh` against the repository itself ⟦criterion 1⟧
- [ ] `prose-owed.sh .` exits 0 and the full `make test` is green ⟦full-suite⟧ ⟦criterion 5⟧

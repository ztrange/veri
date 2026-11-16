# Plan for #3992 — PRD 021.18: `invisible-work.sh` reports new commits on a reused branch name

- [x] a local branch not on origin whose name a CLOSED PR used, its tip a commit other than that PR's head sha, is reported under invariant 1; a small case in `tests/py/unit/test_invisible_work.py` ⟦criterion 1⟧
- [x] the same branch with its tip equal to a MERGED or CLOSED PR's head sha is still skipped; a small case in `tests/py/unit/test_invisible_work.py` ⟦criterion 2⟧
- [x] the `invisible-work.sh` line of `skills/tdd/scripts/veri/README.md` states the rule ⟦criterion 3⟧

# Plan for #4124 — PRD 032.8: a run reports the mutual references among the files it touched

- [x] `coupling.sh <base>` prints `mutual: <a> <b>` for each same-extension non-test code pair, one changed in the range, naming each other, and exits 0 ⟦criterion 1⟧
- [x] `coupling.sh` exits 3 printing nothing with no pair, and 2 with one stderr line when the base does not resolve ⟦criterion 2⟧
- [x] a process case in a scratch repo prints only `mutual: a.py b.py` ⟦criterion 3⟧
- [x] `refactor-owed.sh not-done` accepts `coupling`; `refactor-candidates.sh` lists it, `list` does not ⟦criterion 4⟧
- [ ] a second `coupling` row replaces the first, so a resume never adds one ⟦criterion 5⟧
- [ ] `DRAFT-PR.md` runs `coupling.sh` after the structural pass and before `refactor-candidates.sh`, the `### Coupling` section and the one `coupling` row; rows graded ⟦criterion 5⟧
- [ ] `SCRIPTS.md` has a `coupling.sh` entry; rows graded ⟦criterion 6⟧

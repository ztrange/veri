# Plan for #4121 — PRD 032.6: a run refuses to ready a PR that adds a file nothing calls

- [x] `unwired.sh <base>` prints each added non-test file outside `.tdd/` whose stem no other non-test file names as a whole word, and exits 1 ⟦criterion 1⟧
- [ ] `unwired.sh` exits 0 printing nothing when every added non-test file is named, and 3 when the range adds none ⟦criterion 2⟧
- [ ] `unwired.sh` exits 2 with one stderr line when the base does not resolve or the directory is not a git work tree ⟦criterion 3⟧
- [ ] the stem inside the added file itself does not count as a caller ⟦criterion 4⟧
- [ ] a process case in a scratch repo prints only `src/orphan.py` and exits 1 ⟦criterion 5⟧
- [ ] `classify-bail.sh unwired` prints `process` ⟦criterion 6⟧
- [ ] `unreachable.sh` unchanged and called by no procedure file ⟦criterion 7⟧
- [ ] `DRAFT-PR.md` runs `unwired.sh` after `refactor-candidates.sh` and before readying; `BAIL.md` names `unwired`; `SCRIPTS.md` has its entry; rows graded ⟦criterion 8⟧

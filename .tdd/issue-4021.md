# Plan for #4021 — PRD 030.5: `report-owed.json` is safe to read

- [x] `report.sh --store-owed` writes the new file under a temporary name in `.tdd/` and renames it over `report-owed.json`; a failed rename leaves the previous file byte-identical, no temporary file in `.tdd/`, and exits 2 ⟦criterion 1⟧
- [x] run from a linked worktree or a subdirectory, `--store-owed` writes, and `--stale` and `--report` read, `<main working tree>/.tdd/report-owed.json` ⟦criterion 2⟧
- [ ] with no `report-owed.json`, `--stale` prints the number of every active PRD and exits 0, and `--report` prints `owed: stale` for each ⟦criterion 3⟧
- [ ] each stored entry carries `computedAt`, the UTC time of the store as `YYYY-MM-DDTHH:MM:SSZ`; an entry without it is read as before ⟦criterion 4⟧
- [ ] `--store-owed` exits 2 naming the answer file, `report-owed.json` byte-identical, when the answer is not an object holding `count`, a whole number >= 0, and `sections`, a list of strings ⟦criterion 5⟧
- [ ] a case fails, naming the key, when the keys of `PUBLISHED.md`'s `report-owed.json` example differ from those of a file `--store-owed` writes ⟦criterion 6⟧
- [ ] `PUBLISHED.md` states the file's path, writer, whole-file replacement, missing file, current or stale entry and `computedAt`, and `SCRIPTS.md`'s `report.sh --report` entry the main-tree path, the whole-file replacement, the wrong-shape exit 2 and `--stale` on a missing file ⟦criterion 7⟧ ⟦criterion 8⟧

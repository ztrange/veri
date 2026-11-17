# Plan for #4108 — PRD 031.2: a region counts as surrounded only when every mutant goes red

- [ ] `VERI_SURROUND_MUTANTS` is a `TUNABLES` entry, a whole number at least 1, default 5 ⟦criterion 5⟧
- [ ] `surround-mutants.sh <report-file>… -- <command…>` runs each `MUTANT:` row through `mutation-probe.sh` and prints one line per row ending `red`, `survived` or `no-answer` ⟦criterion 1⟧
- [ ] it exits 0 when every row is red and there are at least `VERI_SURROUND_MUTANTS` rows, 1 on a survivor ⟦criterion 2⟧
- [ ] it exits 1 with last line `short <k> of <N>` when every row is red but too few ⟦criterion 3⟧
- [ ] it exits 2 for no command, an unreadable report, a malformed `MUTANT:` line, a row the probe answered 2, or a bad `VERI_SURROUND_MUTANTS` ⟦criterion 4⟧ ⟦criterion 5⟧
- [ ] a process case runs the shim over the real `mutation-probe.sh` in a scratch repo ⟦criterion 1⟧
- [ ] `classify-bail.sh surround-short` prints `process` ⟦criterion 6⟧
- [ ] docs: `develop-surround.md`, `verify-surround.md`, `LEGACY.md`, `BAIL.md`, `SCRIPTS.md`, CLAUDE.md, rows and grades ⟦criterion 7⟧ ⟦criterion 8⟧ ⟦criterion 9⟧

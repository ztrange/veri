# Plan for #4204 — PRD 035.2: the metrics of every issue are a published file, kept current

- [x] after an `exit`, `step-done`, `bail` or `done` event with an issue, `<issue>.metrics.json` beside the journal holds the `--json` object of that issue, the line included ⟦criterion 1⟧
- [x] an event of any other name leaves the file's bytes, and its absence, unchanged ⟦criterion 2⟧
- [ ] the file is written under a temporary name in its directory and renamed; a failed rename leaves the previous file intact and no partial one ⟦criterion 3⟧
- [ ] a fold or write failure leaves the event written and its exit unchanged, with one stderr line naming the file and the error ⟦criterion 4⟧
- [ ] the fold of a journal alone writes the file with every figure needing a missing file `null`, and two runs in one journal make one file ⟦criterion 5⟧
- [ ] an event with no issue, or in a clone with no `origin`, writes no metrics file and prints nothing about it ⟦criterion 6⟧
- [ ] `PUBLISHED.md` lists the metrics file as a third published file (PB1 reworded, PB12, PB13), graded ⟦criterion 7⟧
- [ ] a case names the key when the `--json` object's keys and those `PUBLISHED.md` states for the metrics file differ ⟦criterion 8⟧
- [ ] `run_conductor.py` handles a conductor's exit the same with the metrics file's directory not writable ⟦criterion 9⟧

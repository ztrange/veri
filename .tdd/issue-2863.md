# Plan for #2863 — tests_frozen's Go case body runs past the case's closing brace, so a helper defined after the case counts twice and leaves the record stale

- [x] Go, helper defined after the last case: a case recorded at its verified green, refactored with the same assertions, then `rerecord-refactored` then `check-earlier` exits 0, the Go case body ending at its first column-0 closing brace ⟦criterion 1⟧
- [x] Go, helper defined between two cases: `rerecord-refactored` then `check-earlier` exits 0 ⟦criterion 2⟧
- [x] Go, a helper appended at EOF after the re-record leaves `check-earlier` at 0 ⟦criterion 3⟧
- [x] Go, deleting an assertion from a case still leaves `check-earlier` at 1 ⟦criterion 4⟧
- [ ] Go, a verified refactor that moves assertions into a helper the case calls, defined after the case, and drops one of them before the re-record: `rerecord-refactored` leaves the record and `check-earlier` exits 1 (an assertion deleted from a helper after the re-record is out of scope, as for a helper defined before the case) ⟦added⟧ ⟦criterion 4⟧
- [ ] Go, a format-2 record cut under the old form (digest of the body running past the closing brace, unchanged since) passes `check-earlier` ⟦criterion 5⟧
- [ ] Go, a run holding an old-form record heals it: `rerecord-refactored` rewrites it to the new cut and `check-earlier` then exits 0 ⟦criterion 5⟧
- [ ] `rerecord-refactored` prints one stderr line `skipped: <file> <case>` naming each case it left unrecorded, and still exits 0 ⟦criterion 6⟧
- [ ] Go-red control: with `_cases` reverted to the old cut, the after-the-last-case and between-two-cases cases go red, watched and restored ⟦human-owed⟧ ⟦criterion 7⟧

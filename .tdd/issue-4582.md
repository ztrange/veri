# Plan for #4582 — near-duplicates.sh lists the blocks a step's commit added that repeat code elsewhere in the files it touched

- [ ] `near-duplicates.sh <commit>` prints one line `<file>:<first>-<last> <file>:<first>-<last>`, the added block first, when a function added between `<commit>^` and `HEAD` repeats 3 or more consecutive counting lines of an older function in the same file under different identifier names and indentation, and exits 0 ⟦criterion 1⟧
- [ ] `near-duplicates.sh <commit>` finds the older copy in another file `<commit>` touched ⟦criterion 2⟧
- [ ] `near-duplicates.sh <commit>` does not report an older copy in a file `<commit>` did not touch ⟦criterion 2⟧
- [ ] `near-duplicates.sh <commit>` prints no pair neither side of which holds a line added between `<commit>^` and `HEAD`, over a file that already held two copies ⟦criterion 3⟧
- [ ] `near-duplicates.sh <commit>` prints nothing for a run of matching lines with fewer than 3 lines holding a letter or a digit, however many brace-only or blank lines it spans ⟦criterion 4⟧
- [ ] `near-duplicates.sh <commit>` prints one line for one maximal 6-line repeat, not one per 3-line window ⟦criterion 5⟧
- [ ] `near-duplicates.sh <commit>` never pairs a test file, the only repeat being between two test files ⟦criterion 6⟧
- [ ] `near-duplicates.sh <commit>` exits 3 printing nothing when it finds no pair ⟦criterion 7⟧
- [ ] `near-duplicates.sh` with no `<commit>` exits 2 with a usage line on stderr ⟦criterion 7⟧
- [ ] `near-duplicates.sh <commit>` with an unresolvable `<commit>` exits 2 with a usage line on stderr ⟦criterion 7⟧
- [ ] `skills/tdd/SCRIPTS.md` has a `near-duplicates.sh` entry under a new SC row in `skills/tdd/REQUIREMENTS.md`, graded PASS ⟦criterion 8⟧

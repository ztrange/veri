# Plan for #1725 — PRD 011 S3: a PASS writes a signature, and make unit fails on prose whose signature no longer matches

- [x] A unit's signature, a sha256 computed in-process by grade_prose (no new script), changes when the unit's text changes and does not change when only a `Why` cell of its requirements list changes ⟦criterion 1⟧
- [x] A unit's signature changes when any `ID` cell or any `Requirement` cell of its requirements list changes ⟦criterion 1⟧
- [x] A unit's signature changes when the grader prompt template changes, and when the model in `skills/tdd/grader.conf` changes ⟦criterion 1⟧
- [x] When every requirement PASSes, `grade-prose.sh` writes one line for the unit to `skills/<skill>/GRADED` carrying the unit, its signature, the date and the id of the grading's event (the `grading` event carries that id) — pinned by a case with a stub `claude` ⟦criterion 2⟧
- [x] A PASS replaces any earlier `GRADED` line for the same unit, leaving the lines of other units as they were, so the file holds one line per unit — pinned by a case with a stub `claude` ⟦criterion 2⟧
- [x] A REJECT, and an exit 2 (no verdict), leave `GRADED` byte-identical — pinned by a case with a stub `claude` ⟦criterion 2⟧
- [x] A new `prose-owed.sh <repo-root>` (a `/bin/sh` shim over a `veri/` module, with a no-argument usage line and exit 2, its SCRIPTS.md entry, and called from the Makefile's `test unit` recipe so `make unit` and `make test` run it) prints nothing and exits 0 on a tree where no unit has a requirements list ⟦criterion 3⟧
- [x] `prose-owed.sh` prints a unit that has a requirements list but no `GRADED` line, and exits 1 ⟦criterion 3⟧
- [x] `prose-owed.sh` prints a unit whose current signature differs from its `GRADED` line and exits 1, and does not print a unit whose `GRADED` signature matches ⟦criterion 3⟧
- [x] `prose-owed.sh` prints each `GRADED` line whose unit no longer exists, marked as an orphan, and exits 1 ⟦criterion 3⟧
- [x] `prose-owed.sh` never prints a unit with no requirements list, even one named in a file that has no `GRADED` line ⟦criterion 3⟧
- [x] `make unit` (and so `make test`) fails, naming each unit `prose-owed.sh` prints, when it prints anything — pinned by a case ⟦criterion 4⟧
- [x] `grade-prose.sh --owed` grades exactly the non-orphan units `prose-owed.sh` prints, and no others — pinned by a case with a stub `claude` ⟦criterion 5⟧
- [x] The owed check `make unit` and `make test` run launches no grader leaf: `prose-owed.sh` run in-process with process launches spied records no launch — pinned by a case ⟦criterion 6⟧

### When every requirement PASSes, `grade-prose.sh` writes one line for the unit to `skills/<skill>/GRADED` carrying the unit, its signature, the date and the id of the grading's event (the `grading` event carries that id) — pinned by a case with a stub `claude` ⟦criterion 2⟧
- `record_graded` only appends; criterion 2's "replacing any earlier line for that unit" belongs to a later step, so don't pre-build it here
### `prose-owed.sh` prints a unit whose current signature differs from its `GRADED` line and exits 1, and does not print a unit whose `GRADED` signature matches ⟦criterion 3⟧
- test-only | extract the repeated `subprocess.run([prose-owed.sh, tmp_path], ...)` call in test_prose_owed_process.py into a helper
- test-only | extract the repeated REQUIREMENTS.md table fixture string in test_prose_owed_process.py
### `grade-prose.sh --owed` grades exactly the non-orphan units `prose-owed.sh` prints, and no others — pinned by a case with a stub `claude` ⟦criterion 5⟧
- share one helper for the `GRADED` path (`os.path.join(os.path.dirname(unit.partition("#")[0]), "GRADED")`) between `grade_prose.record_graded` and `prose_owed.graded_signature`

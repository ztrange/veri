### `refactor-owed.sh append` keeps a `CANDIDATES: test-only` candidate in the owed file under its step's heading ⟦criterion 2⟧
- the new `test-only` regex in `refactor-owed.sh` append copies `structural_candidate`'s pattern from `lib/candidate-line.sh` with only the class word changed. Fold the two into one class-parameterised helper in that lib. Step 6 (`refactor-triage.sh`) will need the same parse, so that is when a second caller justifies it.
- `refactor-owed.sh` append now puts test-only transforms into the array named `structural`, so the name is wrong. Split it into its own array when step 3 (`list` never prints test-only) forces the two classes apart.
### `refactor-owed.sh list` never prints a test-only candidate, and an owed file holding only test-only candidates makes `list` exit 3 with nothing on stdout ⟦criterion 2⟧
- rename the `structural` array in refactor-owed.sh append, which now also holds `test-only | …` entries
- move the `CANDIDATES: test-only` regex in refactor-owed.sh append into lib/candidate-line.sh beside structural_candidate
### `refactor-owed.sh render` prints the test-only candidates under a heading of their own inside `## Refactor owed`, saying the structural pass does not work them ⟦criterion 4⟧
- fold the two render cases' shared capture (`rendered="$(mktemp)"`, `render … && code=0 || code=$?`, the exit-0 check) in `tests/refactor-owed.test.sh` into one helper
- append's `test-only` match is a second hand-written regex beside `structural_candidate` in `lib/candidate-line.sh`; give it a `test_only_candidate` there (cross-file, so out of scope here)

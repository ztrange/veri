# Plan for #1772 — tests-frozen.sh record --step misses a test file Red deleted, so check --step blames the deletion on Green

- [x] After Red deletes a tracked test file and `tests-frozen.sh record --step` runs, `check --step` exits 0 when that deletion is the only change outside the record (the record holds the file as deleted) ⟦criterion 1⟧ ⟂ refactor pending
- [ ] A test file the `record --step` record holds as deleted that exists again at `check --step` makes `check --step` exit 1, naming that file on stdout ⟦criterion 2⟧
- [ ] A tracked test file deleted after `record --step` ran (absent from the record) still makes `check --step` exit 1, naming that file on stdout ⟦criterion 2⟧
- [ ] `skills/tdd/SCRIPTS.md`'s `tests-frozen.sh` entry describes both behaviours: `record --step` records a test file Red deleted as deleted, and `check --step` exits 1 naming a file recorded as deleted that exists again, and still names a tracked test file deleted after the record ⟦diff-checked⟧ ⟦criterion 3⟧

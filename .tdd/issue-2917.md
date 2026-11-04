# Plan for #2917 — A step's tick re-records a renamed case when run from a subdirectory of the repo

- [x] Ticking a step with `tick-ledger.sh --refactor-pending` from a subdirectory of the repo, after a case recorded by `tests-frozen.sh record --step` was renamed in the uncommitted work tree, leaves the step's frozen-cases record holding the renamed title and exits 0 (the record and the test file it names are found from the repo's top level, not the cwd) ⟦criterion 1⟧ ⟂ refactor pending
- [ ] Ticking the same step with `tick-ledger.sh --refactor-pending` from a subdirectory of the repo and from the repo root, after the same rename, leaves byte-identical frozen-cases records ⟦criterion 2⟧
- [ ] Go-red: with the record lookup made cwd-relative again, the subdirectory case fails ⟦human-owed⟧ ⟦criterion 3⟧

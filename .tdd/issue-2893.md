# Plan for #2893 — PRD 017.1: Go, JS spec and Python test files anywhere count as test files when production is frozen or a transform checked

- [ ] The case `test_main_counts_a_path_as_a_test_file_by_the_case_sensitive_ere_on_the_path_as_git_prints_it` in skills/tdd/scripts/tests/py/test_transform_touches_tests.py no longer lists `foo_test.go` among its ignored paths, so it pins neither answer for a Go test file; nothing else in it changes and no production file changes ⟦diff-checked⟧
- [ ] `production-frozen.sh` exits 0, printing no path, on a range changing only `pkg/x_test.go`, and likewise on a range changing only each of `src/foo.spec.ts`, `src/test_foo.py` and `pkg/foo_test.py` (a process case with a real git repo in skills/tdd/scripts/tests/py/test_production_frozen_process.py); the shared test-file check reads a path's basename for the Go `_test.go`, Python `test_*.py` / `*_test.py` and JS `.spec.` names ⟦criterion 1⟧
- [ ] `transform-touches-tests.sh` exits 1, naming the file, on a range changing `pkg/x_test.go`, and likewise on a range changing each of `src/foo.spec.ts`, `src/test_foo.py` and `pkg/foo_test.py` ⟦criterion 2⟧
- [ ] `production-frozen.sh` still exits 1, naming it, on a range changing `pkg/x.go` ⟦criterion 3⟧
- [ ] `transform-touches-tests.sh` still exits 0 on a range changing only `pkg/x.go` ⟦criterion 3⟧
- [ ] `echo 'CANDIDATES: structural | t' | refactor-owed.sh append <file> S 'pkg/x_test.go,src/foo.spec.ts'` prints `- test-only | t`, as it already does for `src/a.test.js` ⟦criterion 4⟧

### `transform-touches-tests.sh`, when `git log <base-sha>..HEAD` fails although `<base-sha>` resolves to a commit (e.g. a missing object in the range), exits 2 — never 0 ⟦criterion 2⟧
- test-only | rename `test_main_ports_the_failure_paths_as_they_are_swallowed_git_log_closed_stdout…` in `tests/py/test_transform_touches_tests.py`: its git-log case now asserts exit 2, so "swallowed" no longer describes it
- test-only | add the "exit 2 when the range cannot be read" line to the `Contract under test` header in `tests/transform-touches-tests.test.sh`, which still lists only exits 1 and 0

# Plan for #3929 — PRD 023.17: wrong_test_route's logic is tested once, in-process, and its shim once

- [x] every case of test_wrong_test_route_process.py runs in-process through run_cli in unit/test_wrong_test_route.py, with the same argv, environment and cwd and the same asserted exit code, stdout and stderr ⟦criterion 1⟧
- [x] every moved case is small: no process or tree_audit mark, and fast_tier_guard names none ⟦criterion 3⟧
- [x] a probe breaking one exit path of wrong_test_route.main turns a moved case red ⟦criterion 4⟧
- [x] test_wrong_test_route_process.py keeps only entry-point cases: exit 0, 1, 2 and 3 passed through, --help prints the usage ⟦criterion 2⟧

# Plan for #3927 — PRD 023.15: parked_issues's logic is tested once, in-process, and its shim once

- [x] every logic case of test_parked_issues_process.py runs in-process through run_cli in unit/test_parked_issues.py, with the same argv, stdin, cwd and asserted exit code, stdout and stderr, each gh stub answering the same calls through fake_processes ⟦criterion 1⟧
- [x] every moved case is small: no process or tree_audit mark, and fast_tier_guard names none ⟦criterion 3⟧
- [x] a probe breaking one exit path of parked_issues.main turns a moved case red ⟦criterion 4⟧
- [x] test_parked_issues_process.py keeps only entry-point cases: exit 0, 2 and 3 passed through, --help prints the usage ⟦criterion 2⟧

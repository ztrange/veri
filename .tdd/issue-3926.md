# Plan for #3926 — PRD 023.14: run_finished's logic is tested once, in-process, and its shim once

- [ ] every logic case of test_run_finished_process.py runs in-process through run_cli in unit/test_run_finished.py, with the same argv, stdin, cwd and asserted exit code, stdout and stderr, git and gh faked at their process boundary ⟦criterion 1⟧
- [ ] every moved case is small: no process or tree_audit mark, and fast_tier_guard names none ⟦criterion 3⟧
- [ ] a probe breaking one exit path of run_finished.main turns a moved case red ⟦criterion 4⟧
- [ ] test_run_finished_process.py keeps only entry-point cases and the running-run case: exit 0, 1 and 2 passed through, --help prints the usage ⟦criterion 2⟧

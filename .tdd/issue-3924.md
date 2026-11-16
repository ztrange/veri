# Plan for #3924 — PRD 023.12: prose_owed's logic is tested once, in-process, and its shim once

- [x] every logic case of test_prose_owed_process.py runs in-process through run_cli in unit/test_prose_owed.py, with the same argv, stdin, env, cwd and asserted exit code, stdout and stderr ⟦criterion 1⟧
- [x] every moved case is small: no process or tree_audit mark, and fast_tier_guard names none ⟦criterion 3⟧
- [x] a probe breaking one exit path of prose_owed.main turns a moved case red ⟦criterion 4⟧
- [ ] the thirteen audits of this repository's graded prose leave the process file unchanged, for test_prose_owed_repo_audit_process.py: in-process, the waiver's git against this repository is refused
- [ ] test_prose_owed_process.py keeps only entry-point cases: exit 0, 1 and 2 passed through, --help prints the usage ⟦criterion 2⟧

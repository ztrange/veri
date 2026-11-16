# Plan for #3923 — PRD 023.8: requirements's logic is tested once, in-process, and its shim once

- [x] every logic case of test_requirements_process.py runs in-process through run_cli in unit/test_requirements.py, with the same argv, stdin, env, cwd and asserted exit code, stdout and stderr ⟦criterion 1⟧
- [x] every moved case is small: no process or tree_audit mark, and fast_tier_guard names none ⟦criterion 3⟧
- [x] a probe breaking one exit path of requirements.main turns a moved case red ⟦criterion 4⟧
- [ ] test_requirements_process.py keeps only entry-point cases: exit 0 and exit 2 passed through, --help prints the usage ⟦criterion 2⟧

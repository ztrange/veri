# Plan for #3925 — PRD 023.13: rerun_alone's logic is tested once, in-process, and its shim once

- [x] every logic case of test_rerun_alone_process.py runs in-process through run_cli in unit/test_rerun_alone.py, with the same argv, stdin, env, cwd and asserted exit code, the alone command faked at `sh` and its targets asserted as the argv `sh` receives ⟦criterion 1⟧
- [x] every moved case is small: no process or tree_audit mark, and fast_tier_guard names none ⟦criterion 3⟧
- [x] a probe breaking one exit path of rerun_alone.main turns a moved case red ⟦criterion 4⟧
- [ ] test_rerun_alone_process.py keeps only entry-point cases: exit 0 and exit 2 passed through, --help prints the usage ⟦criterion 2⟧

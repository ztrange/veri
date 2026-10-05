# Plan for #818 — veri's exit-code contract holds in run-affordable and transform-touches-tests

- [x] `run-affordable.sh`, when `step-cost.sh --steps` fails with a status other than 0 or 3 (e.g. 1, from an uncaught exception), exits 2 with nothing on stdout ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `transform-touches-tests.sh`, when `git log <base-sha>..HEAD` fails although `<base-sha>` resolves to a commit (e.g. a missing object in the range), exits 2 — never 0 ⟦criterion 2⟧
- [ ] every case each script's suites (run-affordable.test.sh, skill-run-affordable.test.sh, tests/unit/run-affordable.test.sh, test_run_affordable.py, transform-touches-tests.test.sh, test_transform_touches_tests.py) already hold passes ⟦full-suite⟧ ⟦criterion 3⟧
- [ ] the branch's diff changes no existing assertion in those suites, except one that pinned the very outcome criterion 1 or 2 fixes, changed only to that criterion's expected exit code (and stdout/stderr where the criterion names it) ⟦diff-checked⟧ ⟦criterion 3⟧

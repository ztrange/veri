# Plan for #2946 — suite-red-resume.sh usage line never names the flake subcommand

- [x] A `flake` call to suite-red-resume with the wrong argument count (e.g. `flake only-one-arg`) exits 2 and its stderr usage line names `flake`; a unit case in tests/py/unit/test_suite_red_resume.py driven in-process with run_cli pins it, failing against today's USAGE ⟦criterion 2⟧
- [ ] `USAGE` in suite_red_resume.py names `check`, `insert` and `flake`, each with its arguments (`flake <at> <red-file> <alone-red-file>`), as the stderr of a no-argument call shows; a unit case in tests/py/unit/test_suite_red_resume.py pins it ⟦criterion 1⟧

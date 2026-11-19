# Plan for #4418 — PRD 036.2: make ceiling measures the highest test-worker count this machine runs without timeouts

- [x] `skills/tdd/scripts/test-ceiling.sh`, a `/bin/sh` shim over `veri/ceiling.py`, with every step green runs `make test`'s full selection once per step at `VERI_PYTEST_WORKERS=<w>` for w = 2, 4, 6, … up to the logical cores, prints the ceiling (the top step) and exits 0; an in-process case faking the suite run ⟦criterion 1⟧
- [x] `--max <n>` ends the ramp at the highest even step not above `<n>`; a missing, non-numeric or below-2 `--max`, or any other argument, is exit 2 with the usage line and no suite run; in-process cases ⟦criterion 1⟧
- [x] a step in which a case fails by its per-case timeout re-runs that case alone with one worker; passing alone, the ramp stops and the ceiling is the last step with no timeout, exit 0; an in-process case driving the recorder plugin with a pytest-timeout report ⟦criterion 2⟧
- [ ] a timed-out case that times out alone too is exit 2 naming it as hung; an in-process case ⟦criterion 2⟧
- [ ] a case failing other than by its per-case timeout is exit 2 naming it, with no re-run; an in-process case driving the recorder plugin with a plain failure ⟦criterion 2⟧ ⟦criterion 6⟧
- [ ] a load timeout at w = 2 is exit 1 printing "no ceiling of at least 2"; an in-process case ⟦criterion 2⟧
- [ ] a suite run that exits non-zero with no failed case recorded (a refusal, a red `prose-owed.sh`) is exit 2 naming its exit code and the workers; an in-process case ⟦added⟧ ⟦criterion 2⟧
- [ ] each step registers its workers under the legs registry (`VERI_PYTEST_LEGS`) for the step's duration, re-runs included, and removes the entry after it; an in-process case ⟦criterion 3⟧
- [ ] a step waits before starting, with one stderr line naming the other legs' pids and workers, while any other live leg is registered; an in-process case ⟦criterion 3⟧
- [ ] on exit 0 the record at `VERI_TEST_CEILING_FILE` (default `~/.veri-test-ceiling`) is replaced whole through a temporary file: the ceiling, the date, the commit, the load average at start, one `<workers> <seconds> <timeouts>` line per step; an in-process case ⟦criterion 4⟧
- [ ] exit 1 and exit 2 leave an earlier record unchanged; in-process cases ⟦criterion 4⟧
- [ ] the `ceiling` `.PHONY` target runs `test-ceiling.sh` and is its one entry point: no `test`/`unit` recipe, CI workflow, procedure file or prompt names it, and `unreachable.sh` does not list it; a tree-audit case ⟦criterion 5⟧
- [ ] CLAUDE.md's Commands table gains the `make ceiling` row and its opening paragraph names `test-ceiling.sh`; SCRIPTS.md, `veri/README.md` and the CM306/CM307 rows land with it, regraded ⟦skill-edit⟧ ⟦criterion 7⟧

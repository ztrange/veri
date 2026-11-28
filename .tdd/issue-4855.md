# Plan for #4855 — pytest leg: leave the run directory in place on CI (VERI_PYTEST_KEEP_RUN_DIR)

- [ ] with VERI_PYTEST_KEEP_RUN_DIR unset, leaving run_directory() removes the run directory and a file planted under its base/, and the case goes red when the cleanup is skipped unconditionally ⟦criterion 3⟧ ⟦criterion 4⟧
- [ ] with VERI_PYTEST_KEEP_RUN_DIR=1, leaving run_directory() leaves the run directory and a file planted under its base/ in place, the knob declared in TUNABLES as choice("0", "1") defaulting to 0 ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 5⟧
- [ ] ci.yml's make test step sets VERI_PYTEST_KEEP_RUN_DIR: "1", every job keeping timeout-minutes and ubuntu-latest ⟦criterion 6⟧
- [ ] tests/py/README.md's The pytest leg states the knob, regraded, prose-owed.sh exits 0 ⟦criterion 7⟧

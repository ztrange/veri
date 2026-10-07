# Plan for #1089 — cover-outcome.sh keeps NUL bytes from its report, where the bash version dropped them

- [x] `report_read` in `veri/report.py` drops NUL bytes from the report text before parsing its KEY: value lines, so a `CAUGHT_BY: a\0b` line reads as `ab` for every port that uses it ⟦criterion 3⟧
- [x] `cover-outcome.sh` given a report whose `CAUGHT_BY:` line is `a\0b` (with `COVERED: yes`) prints `ab` and exits 0 ⟦criterion 1⟧
- [x] `cover-outcome.sh` given a report whose `COVERED:` line is `y\0es` exits 0, as `COVERED: yes` does ⟦criterion 2⟧
- [ ] fix the full-suite failure: skills/tdd/scripts/tests/py/test_comment_class.py — FAILED test_main_sweeps_the_unit_fixture_guard_and_offline_suites_to_empty_sweepable_reports: the sweepable report for tests/unit/[c-e]*.sh is not empty, naming skills/tdd/scripts/tests/unit/cover-outcome.test.sh:107:1 ⟦suite-repair⟧ ⟦criterion 2⟧

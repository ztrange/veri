# Plan for #1089 — cover-outcome.sh keeps NUL bytes from its report, where the bash version dropped them

- [x] `report_read` in `veri/report.py` drops NUL bytes from the report text before parsing its KEY: value lines, so a `CAUGHT_BY: a\0b` line reads as `ab` for every port that uses it ⟦criterion 3⟧
- [x] `cover-outcome.sh` given a report whose `CAUGHT_BY:` line is `a\0b` (with `COVERED: yes`) prints `ab` and exits 0 ⟦criterion 1⟧
- [x] `cover-outcome.sh` given a report whose `COVERED:` line is `y\0es` exits 0, as `COVERED: yes` does ⟦criterion 2⟧

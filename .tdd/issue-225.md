# Plan for #225 — The three docs-record suites duplicate their report/plain/records/bullet/says helpers

- [x] A shared helper file under skills/tdd/scripts/tests/, not named *.test.sh and not picked up by make test's suite glob, when sourced defines report and plain with the same behaviour as the copies in the four *-recorded.test.sh suites that carry them ⟦criterion 1⟧
- [x] The shared helper file, when sourced, also defines records, bullet and says with the same behaviour as the copies in selection-order-recorded.test.sh and model-knobs-recorded.test.sh ⟦criterion 1⟧
- [x] selection-order-recorded.test.sh and model-knobs-recorded.test.sh source the shared file and define no report, plain, records, bullet or says of their own ⟦criterion 1⟧
- [x] lane-rule-recorded.test.sh and unit-tier-recorded.test.sh source the shared file and define no report or plain of their own, while each keeps its own different says ⟦criterion 1⟧
- [x] The shared file sourced from a working directory other than the repo root defines report, plain, records, bullet and says ⟦added⟧ ⟦criterion 2⟧
- [x] Each of the four suites resolves the shared file from the suite own location rather than the working directory, and each still prints its own count line ⟦added⟧ ⟦criterion 2⟧
- [x] No suite gains a dependency outside the repo, and the shared file keeps the plain-shell idiom: no test framework, each suite keeps its own pass/fail counters, FAIL - lines and count line ⟦criterion 3⟧
- [ ] The Green comment records, for selection-order-recorded.test.sh and model-knobs-recorded.test.sh, which guarded passage was broken and the FAIL - line, failed count and non-zero exit observed ⟦added⟧ ⟦criterion 4⟧
- [ ] The Green comment records, for lane-rule-recorded.test.sh and unit-tier-recorded.test.sh, which guarded passage was broken and the FAIL - line, failed count and non-zero exit observed ⟦added⟧ ⟦criterion 4⟧

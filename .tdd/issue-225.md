# Plan for #225 — The three docs-record suites duplicate their report/plain/records/bullet/says helpers

- [x] A shared helper file under skills/tdd/scripts/tests/, not named *.test.sh and not picked up by make test's suite glob, when sourced defines report and plain with the same behaviour as the copies in the four *-recorded.test.sh suites that carry them ⟦criterion 1⟧
- [x] The shared helper file, when sourced, also defines records, bullet and says with the same behaviour as the copies in selection-order-recorded.test.sh and model-knobs-recorded.test.sh ⟦criterion 1⟧
- [ ] selection-order-recorded.test.sh and model-knobs-recorded.test.sh source the shared file and define no report, plain, records, bullet or says of their own ⟦criterion 1⟧
- [ ] lane-rule-recorded.test.sh and unit-tier-recorded.test.sh source the shared file and define no report or plain of their own, while each keeps its own different says ⟦criterion 1⟧
- [ ] Each of the four suites still runs standalone as bash <suite> from any working directory and its output still ends in its own <n> passed, <m> failed count line ⟦criterion 2⟧
- [ ] No suite gains a dependency outside the repo, and the shared file keeps the plain-shell idiom: no test framework, each suite keeps its own pass/fail counters, FAIL - lines and count line ⟦criterion 3⟧
- [ ] Breaking a passage that selection-order-recorded.test.sh or model-knobs-recorded.test.sh guards turns that suite red: a FAIL - line, a non-zero failed count and a non-zero exit, reported through the shared report ⟦criterion 4⟧
- [ ] Breaking a passage that lane-rule-recorded.test.sh or unit-tier-recorded.test.sh guards turns that suite red: a FAIL - line, a non-zero failed count and a non-zero exit, reported through the shared report with their local says ⟦criterion 4⟧

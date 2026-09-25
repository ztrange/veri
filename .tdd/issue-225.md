# Plan for #225 — The three docs-record suites duplicate their report/plain/records/bullet/says helpers

- [ ] A shared helper file under skills/tdd/scripts/tests/, not named *.test.sh and not picked up by make test's suite glob, when sourced defines report, plain, records, bullet and says with the same behaviour as the copies in selection-order-recorded.test.sh and model-knobs-recorded.test.sh ⟦criterion 1⟧
- [ ] The four *-recorded.test.sh suites that carry report and plain (lane-rule, model-knobs, selection-order, unit-tier) source the shared file and define no report or plain of their own; selection-order and model-knobs define no records, bullet or says of their own; lane-rule's and unit-tier's different says stay local ⟦criterion 1⟧
- [ ] Each of the four suites still runs standalone as bash <suite> from any working directory and its output still ends in its own <n> passed, <m> failed count line ⟦criterion 2⟧
- [ ] No suite gains a dependency outside the repo, and the shared file keeps the plain-shell idiom: no test framework, each suite keeps its own pass/fail counters, FAIL - lines and count line ⟦criterion 3⟧
- [ ] With the shared helpers, a fixture document whose guarded passage has been removed or altered makes records and says report a failure, so breaking a passage a suite guards still turns that suite red ⟦criterion 4⟧

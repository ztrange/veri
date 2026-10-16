# Plan for #1634 — PRD 009: the bash fast tier refuses a suite that runs real scripts as subprocesses

- [ ] The unit-tier admission guard fails when a planted suite under tests/unit/ runs a script under skills/tdd/scripts/ as a subprocess rather than sourcing it and mocking what it shells out to, naming that suite as `<suite>:<line>` ⟦criterion 1⟧
- [ ] The unit-tier admission guard lets a planted subprocess-running `<suite>:<line>` through only when its exemption-table entry carries a reason, and fails naming the entry when the reason is empty ⟦criterion 1⟧
- [ ] Every suite under skills/tdd/scripts/tests/unit/ that the admission guard names either meets the bar (sources the script and mocks what it shells out to) or moves to skills/tdd/scripts/tests/, where `make test` still runs it with the same case count; CLAUDE.md's unit-tier suite counts and admission-bar sentence are updated to match ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] The unit-tier admission guard passes over the real skills/tdd/scripts/tests/unit/, naming no offender ⟦criterion 2⟧

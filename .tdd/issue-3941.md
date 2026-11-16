# Plan for #3941 — PRD 017.2: suite-reported and coverage-blocker read reports through report.py

- [ ] suite_reported.py finds SUITE: and an exempt format's keys through report.py, with no line-start match of its own; its cases pass unedited ⟦criterion 1⟧ ⟦criterion 2⟧
- [ ] coverage_blocker.py finds COVERED: no and its MUTATION: lines through report.py, with no line-start or exact-line match of its own; its cases pass unedited ⟦criterion 1⟧ ⟦criterion 2⟧

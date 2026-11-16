# Plan for #3939 — PRD 017.2: report.py reads every report-line rule, and wrong-test-route reads through it

- [ ] report.py reads a report's KEY: lines from text or bytes, the caller choosing first, last or every occurrence, whether a space must follow the colon, and whether a `- ` or `* ` bullet may precede the key; report_read's callers see unchanged results ⟦criterion 1⟧
- [ ] wrong_test_route.py reads every report line through report.py and holds no _lines_with or _report_lines; its cases pass unedited ⟦criterion 2⟧ ⟦criterion 3⟧

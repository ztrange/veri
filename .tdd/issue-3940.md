# Plan for #3940 — PRD 017.2: same-reject, comment and parse-adjudication read reports through report.py

- [ ] same_reject.py finds its first REASON: line through report.py; its cases pass unedited ⟦criterion 1⟧ ⟦criterion 2⟧
- [ ] parse_adjudication.py finds its last ADJUDICATION: line through report.py; its cases pass unedited ⟦criterion 1⟧ ⟦criterion 2⟧
- [ ] comment.py reads its report keys and its RESULT: and FLAGS: lines through report.py, with no line-start match or ": " split of its own; its cases pass unedited ⟦criterion 1⟧ ⟦criterion 2⟧

# Plan for #2896 — PRD 017.1: a renamed Go or JS case is recognised as a rename

- [x] `renamed_to` returns the new name for a Go `func TestX` case renamed with its body unchanged, pinned by a small unit-tier case in skills/tdd/scripts/tests/py/unit/test_renamed_case.py calling `renamed_case.renamed_to` in-process ⟦criterion 1⟧
- [ ] `renamed_to` returns the new title for a JS `it("…")`/`test("…")` case renamed with its body unchanged, pinned by a small unit-tier case in skills/tdd/scripts/tests/py/unit/test_renamed_case.py calling `renamed_case.renamed_to` in-process ⟦criterion 2⟧
- [ ] `renamed_and_changed_to` returns the new name for a Go `func TestX` case renamed with its body changed as well, pinned by a small unit-tier case in skills/tdd/scripts/tests/py/unit/test_renamed_case.py ⟦criterion 3⟧
- [ ] `renamed_and_changed_to` returns the new title for a JS `it("…")`/`test("…")` case renamed with its body changed as well, pinned by a small unit-tier case in skills/tdd/scripts/tests/py/unit/test_renamed_case.py ⟦criterion 3⟧
- [ ] `renamed_to` returns None for a Go or JS case renamed with its body changed as well, pinned by a small unit-tier case in skills/tdd/scripts/tests/py/unit/test_renamed_case.py ⟦criterion 3⟧

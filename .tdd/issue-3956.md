# Plan for #3956 — PRD 017.13: the deleted-case refusal says "test cases"

- [ ] `verify.sh diff` on a step deleting a case an earlier step added prints `step deleted test cases an earlier step added: ` followed by the same case list, and exits 1 ⟦criterion 1⟧ ⟦criterion 3⟧
- [ ] `verify.sh diff` on a step renaming and changing a case an earlier step added prints `step renamed and changed test cases, so the step must be split: ` followed by the same case list, and exits 1 ⟦criterion 2⟧ ⟦criterion 3⟧

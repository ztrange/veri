# Plan for #1486 — verify-diff PASSes a ⟦diff-checked⟧ step that deletes an earlier criterion's evidence

- [x] verify.sh diff exits 1 without launching the verifier leaf, its stdout reason naming `<file>::<case>`, when a pytest case (`def test_…` in a `test_*.py`) absent at the branch-base sha and present at the step-base sha is absent from every test file at HEAD ⟦criterion 1⟧
- [ ] verify.sh diff does not trip on a case an earlier step added and this step moved to another `test_*.py` file under the same name: the verifier leaf is still launched ⟦criterion 1⟧
- [ ] verify.sh diff exits 2 without launching the verifier leaf when the branch-base sha or the step-base sha cannot be resolved ⟦criterion 1⟧
- [ ] verify.sh diff still launches the verifier leaf and returns its verdict when the step deletes only cases that existed at the branch-base sha ⟦criterion 2⟧

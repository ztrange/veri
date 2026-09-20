# Plan for #355 — verify-red: an error on exactly the name the step introduces is a valid red

- [x] The red verifier prompt states that a run erroring on exactly the name the step introduces — a missing function, script, file, route or field — is a valid red ⟦criterion 1⟧ ⟂ refactor pending
- [ ] The red verifier prompt still states that any other error before an assertion is a REJECT: a typo'd name, a wrong path, a missing fixture, a syntax error in the test ⟦criterion 2⟧
- [ ] The red verifier prompt no longer requires the target test to reach its assertions ⟦criterion 3⟧
- [ ] The red developer prompt says a predicted missing-name error names the missing name in PREDICTED_FAILURE: ⟦criterion 4⟧

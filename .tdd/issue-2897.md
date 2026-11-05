# Plan for #2897 — PRD 017.1: the deleted-case guard sees Go and JS cases

- [x] The diff verifier's deleted-case guard refuses a step that deletes a `func TestX` in a `_test.go` file which an earlier step of the branch added, with the existing refusal text unchanged (`step deleted pytest cases an earlier step added: …`) ⟦criterion 1⟧
- [x] The diff verifier's deleted-case guard refuses a step that deletes an `it("x", …)` case in a `.test.js` file which an earlier step of the branch added, with the existing refusal text unchanged ⟦criterion 2⟧
- [x] The diff verifier's deleted-case guard does not refuse a step that renames a `func TestX` in a `_test.go` file, added by an earlier step, with its body unchanged ⟦criterion 3⟧ ⟂ retired unpinnable

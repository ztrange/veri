# Plan for #2799 — tests_frozen records a Go func Test as a case

- [x] `tests-frozen.sh record` on a `_test.go` file holding `func TestX(t *testing.T)` records it as case `TestX` ⟦criterion 1⟧ ⟂ refactor pending
- [ ] Editing the body of a recorded Go test function `func TestX(t *testing.T)` makes `tests-frozen.sh check-earlier` refuse it, naming case `TestX` and its step ⟦criterion 2⟧

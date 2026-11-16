# Plan for #3921 — PRD 023.7: make test runs one pytest pass

- [x] the two-worker case's assertions hold for `make unit` and `make test` in a case each, every nested `make` bounded below its case's `timeout` mark ⟦criterion 4⟧
- [ ] a `tree_audit` case fails naming the file and line of each `serial` mark under tests/py, and no case carries one; the two-conductor watch case keeps its assertion and `delay=5` ⟦criterion 1⟧ ⟦criterion 3⟧

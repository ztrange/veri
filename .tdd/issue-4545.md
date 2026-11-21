# Plan for #4545 — tests-frozen.sh rerecord-refactored exits 1 when a verified refactor only rewords an assertion's failure message

- [ ] `tests-frozen.sh rerecord-refactored` exits 1 for a Go case whose guarded `t.Fatalf` an Extract Function refactor moved into a helper with its `if` condition changed (`err != nil` became `false`) and its message unchanged ⟦criterion 2⟧
- [ ] `tests-frozen.sh rerecord-refactored` exits 0 and re-records a Go case whose guarded `t.Fatalf` an Extract Function refactor moved into a helper under the same `if` condition with a reworded message ⟦criterion 1⟧

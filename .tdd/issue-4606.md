# Plan for #4606 — tests-frozen.sh rerecord-refactored skips a verified Extract Function whose helper lives in a sibling test file

- [ ] rerecord-refactored re-records, exit 0, a Go case whose guarded http.Get / t.Fatalf lines a verified refactor moved into a helper in a new sibling test file of the same directory ⟦criterion 1⟧
- [ ] check-earlier exits 0 for that case after the re-record ⟦criterion 3⟧
- [ ] rerecord-refactored still skips, exit 1, the same move with the t.Fatalf dropped, while another sibling test file holds that guarded t.Fatalf in a helper the case does not call ⟦criterion 2⟧

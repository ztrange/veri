# Plan for #1023 — refactor-owed.sh list still prints a candidate recorded as applied

- [x] `refactor-owed.sh list` does not print a candidate the owed file records with an `applied | <sha> | <candidate>` line, while still printing the candidates not recorded as applied ⟦criterion 1⟧
- [ ] `refactor-owed.sh list` exits 3 with empty stdout when every structural candidate in the owed file has an `applied | <sha> | <candidate>` record ⟦criterion 2⟧

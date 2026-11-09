# Plan for #3395 — supervise.py: a mutation-record marker followed by punctuation captures it, so the named record is not exempted

- [x] A mutation-record marker in VERI_STEP followed by trailing sentence punctuation (a comma, period, semicolon or closing parenthesis) exempts the record it names from restore_mutation_records, pinned by a unit case that fails on the current code ⟦criterion 1⟧
- [x] A mutation-record marker with no trailing punctuation still exempts the record it names from restore_mutation_records (existing behaviour, kept) ⟦criterion 2⟧
- [ ] A changed mutation record that no marker in VERI_STEP names is still restored by restore_mutation_records (existing behaviour, kept) ⟦criterion 2⟧

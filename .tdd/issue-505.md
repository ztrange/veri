# Plan for #505 — parallel-conductors.sh accepts a non-numeric VERI_MAX_ISSUES and then applies no cap

- [x] parallel-conductors.sh exits 2, naming VERI_MAX_ISSUES and the value, when VERI_MAX_ISSUES is set to a value that is not a whole number >= 1 (a word like abc, zero, a negative, a fraction), and launches no conductor ⟦criterion 1⟧
- [x] parallel-conductors.sh exits 2, naming VERI_MAX_ISSUES, when VERI_MAX_ISSUES is set but empty, and launches no conductor ⟦criterion 2⟧
- [ ] with VERI_MAX_ISSUES unset, parallel-conductors.sh applies no cap and launches every solvable issue, unchanged ⟦criterion 3⟧

# Plan for #1596 — mutation-parity.sh reads proven without checking that the old case and its replacement pass unmutated

- [ ] For a single-case suite, a row whose named old case or replacement already fails with the mutation not applied reads `unproven`, and the output names which of the two failed unmutated ⟦criterion 1⟧
- [ ] For a multi-case suite, a row whose named old case or replacement already fails with the mutation not applied reads `unproven`, and the output names which of the two failed unmutated ⟦criterion 1⟧
- [ ] A suite with more than one case that dies before its count line under the mutation makes mutation-parity.sh end in an error, not print `owed` for that row, pinned by a case that goes red when the multi-case re-raise in veri/mutation_parity.py is replaced by returning `owed` ⟦criterion 2⟧

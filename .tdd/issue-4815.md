# Plan for #4815 — refactor: four row-pin cases read REQUIREMENTS.md directly, with no whole-repo copy or prose_owed run

- [x] the VPL1..VPL27 pin reads the real REQUIREMENTS.md, with no copy, no `prose_owed` run and no `tree_audit` mark ⟦criterion 3⟧
- [ ] the F1/F13/F14 pin reads the real file the same way ⟦criterion 3⟧
- [ ] the RD28 pin reads the real file the same way ⟦criterion 3⟧
- [ ] the SC23 pin reads the real file the same way ⟦criterion 3⟧
- [ ] `test_prd_016_short_names.py` loses the copy-the-tip `prose_owed` case, which pins no row ⟦criterion 1⟧

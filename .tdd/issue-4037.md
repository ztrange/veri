# Plan for #4037 — PRD 025.2: tier-usual.sh is gone

- [x] the over-budget case in test_over_budget_process.py hands over_budget the usual time as the literal 1.0 and imports no veri.tier_usual ⟦criterion 2⟧
- [x] tier-usual.sh, veri/tier_usual.py and their two test files are deleted, their entries leave veri/README.md, unit/test_emitted_text.py and unit/test_scripts_md_rows.py, and git grep tier-usual|tier_usual prints nothing ⟦criterion 1⟧

# Plan for #2288 — run_finished.py reads a ⟦human-owed⟧ mark quoted mid-prose as human-owed, disagreeing with ledger_steps' #1450 rule

- [ ] run-finished.sh decides a PR-body line human-owed by ledger_steps' rule (a leading mark or one in the trailing marker run): an unticked PR-body line quoting the human-owed mark mid-prose ("- [ ] a ⟦human-owed⟧ x") is not listed, while "- [ ] measure X ⟦human-owed⟧" and "- [ ] ⟦human-owed⟧ measure X" still are; pinned by a small in-process case in tests/py/unit/test_run_finished.py ⟦criterion 1⟧

### A stale unit named bare (no backticks) on an unchecked ⟦skill-edit⟧ ledger line is waived: prose-owed.sh exits 0 on a repo whose only stale unit is named bare by the run's ledger ⟦criterion 1⟧
- test-only | the three tests in test_prose_owed_waiver_process.py repeat the same git-init and file-setup block; extract a helper (only files under tests/ change)
### A ⟦skill-edit⟧ line naming the stale unit's path only inside a longer path (the unit path with a suffix such as .bak, or with a leading directory such as x/) does not waive it: prose-owed.sh still exits non-zero ⟦criterion 3⟧
- test-only | extract a shared helper for the repeated git-init, REQUIREMENTS.md, ledger setup and prose-owed.sh run in test_prose_owed_waiver_process.py

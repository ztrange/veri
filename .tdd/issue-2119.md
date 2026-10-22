# Plan for #2119 — The stale-unit waiver misses a ⟦skill-edit⟧ step that names the unit without backticks

- [x] A stale unit named bare (no backticks) on an unchecked ⟦skill-edit⟧ ledger line is waived: prose-owed.sh exits 0 on a repo whose only stale unit is named bare by the run's ledger ⟦criterion 1⟧
- [ ] A stale unit named in backticks on an unchecked ⟦skill-edit⟧ ledger line is still waived: prose-owed.sh exits 0, pinned through its exit code ⟦criterion 2⟧
- [ ] A ⟦skill-edit⟧ line naming the stale unit's path only inside a longer path (the unit path with a suffix such as .bak, or with a leading directory such as x/) does not waive it: prose-owed.sh still exits non-zero ⟦criterion 3⟧

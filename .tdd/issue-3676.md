# Plan for #3676 — role-state.sh coord --lane with no lane value raises IndexError instead of printing usage and exiting 2

- [ ] `role-state.sh coord --lane` with nothing after `--lane` exits 2, prints usage on stderr and writes no state file, instead of raising IndexError ⟦criterion 1⟧
- [ ] The branch adds a case pinning `role-state.sh coord --lane` with no lane value to usage and exit 2, which verify-red saw fail against the unmodified code ⟦diff-checked⟧ ⟦criterion 2⟧

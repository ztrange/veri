# Plan for #3676 — role-state.sh coord --lane with no lane value raises IndexError instead of printing usage and exiting 2

- [x] A case pins that `role-state.sh coord --lane` with nothing after `--lane` exits 2 with usage on stderr instead of raising IndexError, the case seen red against the current code ⟦criterion 2⟧
- [ ] `role-state.sh coord --lane` with nothing after `--lane` exits 2, prints usage on stderr and writes no state file ⟦criterion 1⟧

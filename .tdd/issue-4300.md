# Plan for #4300 — role_growth's malformed-state check is one role_state helper reused by dispatch

- [x] role-growth on a state file holding a line that is neither a field nor an item exits 2 with exactly `malformed state file <path>` and leaves the file unchanged (characterisation) ⟦criterion 4⟧
- [x] the malformed-state check lives in one role_state function that role_growth.main calls, and role_growth names no role_state.Malformed ⟦criterion 1⟧ ⟦criterion 2⟧

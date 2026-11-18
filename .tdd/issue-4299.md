# Plan for #4299 — role_state.refusal reads state lines through State, not hand-parsed key=value

- [x] `request-reset` judges "decided since recovery" against the last of several `recovered-at` lines: a decision after the first recovery but before the last one still refuses it (characterisation, mutant-proven) ⟦criterion 3⟧
- [ ] `State.values(name)` lists the value of every `<name>=<value>` line in file order, skipping other keys and lines with no `=` ⟦criterion 2⟧
- [ ] `refusal()` reads the last `recovered-at` and every `reset-at` through `State.values`, splitting no line on `=` itself; every `request-reset` message and exit code unchanged ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 3⟧

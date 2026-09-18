# Plan for #275 — The pin path never runs the full suite, so a pin that breaks an unrelated suite commits silently

- [ ] SKILL.md's pin PASS branch runs the full suite (the run's <test-cmd>) after verify.sh pin PASSes and before tick-ledger.sh and the `git commit -m "test: pin` line ⟦criterion 1⟧
- [ ] SKILL.md's pin PASS branch says a red full-suite run there bails as a system failure and never commits the pinned step ⟦criterion 2⟧
- [ ] verify-pin.md's check 1 stays scoped to the target test alone, never a full-suite run ⟦criterion 3⟧

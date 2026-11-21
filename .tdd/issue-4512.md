# Plan for #4512 — A ⟦diff-checked⟧ re-pin step whose commits change no test file passes verify-diff and is ticked

- [ ] diff-step.sh leaves a verify-diff REJECT naming the missing test edit, and ticks nothing, on a re-pin step whose commits since its step base change no test file ⟦criterion 1⟧
- [ ] SCRIPTS.md's diff-step.sh entry states the re-pin step's test-edit check, with a requirement row, regraded

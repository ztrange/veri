# Plan for #373 — timed-test-run.sh has no caller, so every run records zero test-run marks

- [x] a developer green prompt names `timed-test-run.sh` at a path the leaf can run, and tells it to run the fast command and the affected suites through that wrapper under the tiers `fast` and `affected` ⟦criterion 1⟧
- [x] the other developer prompts — red, refactor, revise, reconcile — name the same wrapper and the tier each of their test-command runs uses ⟦criterion 1⟧
- [x] a verifier prompt — red, green, refactor, pin — names the same wrapper at a runnable path and the tier each of its test-command runs uses ⟦criterion 1⟧
- [x] a log carrying `test-run` marks renders at least one row under `#### Test-command seconds, by tier` in its metrics ⟦criterion 2⟧
- [ ] `tier-usual.sh` answers with a figure taken from a log carrying `test-run` marks rather than from an empty list ⟦criterion 3⟧
- [ ] a verify-green leaf's target-test run in check 1 also goes through the wrapper, naming tier `target` ⟦criterion 1⟧

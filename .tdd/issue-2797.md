# Plan for #2797 — parse-verdict reads a REASON printed before the verdict and keeps its MISSING_TEST lines

- [x] Output with a `REASON:` line before `VERDICT: REJECT` and nothing after it exits 1 and prints that reason ⟦criterion 1⟧
- [x] Output with `MISSING_TEST: <behaviour>` before `REASON:` and `VERDICT: REJECT` prints both, the `MISSING_TEST:` line intact, so `wrong-test-route.sh` routes on that behaviour ⟦criterion 2⟧
- [ ] Output with a reason after the verdict prints that reason as today, plus any `MISSING_TEST:` line printed before the verdict ⟦criterion 3⟧
- [ ] Output with a `MISSING_TEST:` line before `VERDICT: REJECT`, with no `REASON:` line and nothing after the verdict, prints that `MISSING_TEST:` line intact instead of a blank reason

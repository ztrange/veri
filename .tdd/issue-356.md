# Plan for #356 — A diverged Red prediction sends the step to a red revise instead of verify-red

- [x] `red-divergence.sh` given a report with `PREDICTION: DIVERGED` exits 0 and prints the report's `PREDICTED_FAILURE:`, `FAIL_OUTPUT:` and `PREDICTION_NOTE:` values ⟦criterion 1⟧
- [x] `red-divergence.sh` given a report with `PREDICTION: MATCHED` exits 3 and prints nothing ⟦criterion 2⟧
- [x] `red-divergence.sh` given a report with no `PREDICTION:` line, or a value other than `MATCHED`/`DIVERGED`, exits 2 ⟦criterion 3⟧
- [x] SKILL.md's Red section runs `red-divergence.sh` on the leaf's report and, on exit 0 or 2, skips verify-red and verify-pin, writes `.tdd/verify-red.reason`, emits `prediction-diverged` and enters the red revise loop ⟦criterion 4⟧
- [x] The prompt `build-develop-prompt.sh revise red …` builds ends with `PREDICTED_FAILURE:` and `PREDICTION: MATCHED | DIVERGED` report lines ⟦criterion 5⟧ ⟂ refactor pending
- [ ] SKILL.md's revise loop runs `red-divergence.sh` on a revise-red report before re-verifying, and on exit 0 or 2 spends the next attempt without launching the verifier ⟦criterion 6⟧

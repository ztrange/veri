# Plan for #193 — Red never predicts how the test will fail

- [ ] develop-red.md requires prediction-before-run and carries PREDICTED_FAILURE, PREDICTION, PREDICTION_NOTE in the report footer
- [ ] Pin path in develop-red.md predicts what the temporary break should print and checks it before restoring
- [ ] revise red inherits prediction — a rewritten test owes a new prediction
- [ ] SKILL.md Red comment carries the prediction and whether it matched
- [ ] No verifier prompt contains the prediction — build-verify-prompt.sh takes no rationale parameter, pinned by test

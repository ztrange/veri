# Plan for #193 — Red never predicts how the test will fail

- [x] develop-red.md requires prediction-before-run and carries PREDICTED_FAILURE, PREDICTION, PREDICTION_NOTE in the report footer
- [x] Pin path in develop-red.md predicts what the temporary break should print and checks it before restoring
- [x] revise red inherits prediction — a rewritten test owes a new prediction
- [x] SKILL.md Red comment carries the prediction and whether it matched ⟂ refactor pending
- [ ] No verifier prompt contains the prediction — build-verify-prompt.sh takes no rationale parameter, pinned by test

# Plan for #408 — A step that exhausts its revise budget is evidence the step is too big: ask for SPLIT: before bailing

- [x] build-develop-prompt.sh accepts an `exhausted` phase and renders its template carrying the step, the verifier's last rejection reason and the issue spec, refusing a missing reason file with exit 2 ⟦criterion 1⟧
- [x] exhausted-outcome.sh reads the leaf's report on stdin and answers which of the three outcomes it holds: exit 0 printing the SPLIT: criteria, exit 1 printing the needs-user answer, exit 3 printing nothing when it reports neither ⟦criterion 1⟧
- [x] add-ledger-step.sh takes `instead-of` as a third placement, inserting the texts where the anchor step was and removing that step, under the same VERI_STEP_GROWTH budget and owed-steps refusal ⟦criterion 2⟧
- [x] SKILL.md's revise-exhausted branch launches the exhausted leaf and branches three ways — replace-and-continue on SPLIT:, park on needs-user, and the unchanged revise-exhausted bail on neither ⟦criterion 4⟧
- [ ] the three outcomes are distinguishable marks in the run's event log, and a split reached this way is told apart from a leaf-volunteered one ⟦criterion 5⟧
- [ ] a parked step is mirrored to the issue thread with the leaf's answer and the verifier's last rejection reason, so the user reads why without opening a log ⟦criterion 3⟧

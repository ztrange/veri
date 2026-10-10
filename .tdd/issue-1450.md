# Plan for #1450 — Ledger scripts read ⟦phases⟧ / ⟦criterion⟧ markers inside a step's prose, so a step that quotes the notation is mis-parsed

- [x] ledger-steps.sh reports a step whose prose quotes a criterion marker with only the criterion of its trailing marker run, and a step whose prose quotes a phases marker as a plain open step whose next-phase answer is exit 3 ⟦criterion 1⟧
- [x] ledger-steps.sh reports a step whose prose quotes a full-suite, human-owed or diff-checked kind marker followed by a criterion marker as kind step, keeping the kind only when that marker sits in the trailing marker run ⟦criterion 1⟧ ⟂ refactor pending
- [ ] next-unchecked.sh hands out an open step whose prose quotes a phases marker as an ordinary step, printing its text ⟦criterion 2⟧
- [ ] tick-ledger.sh ticks a step whose prose quotes a phases marker with a plain tick and no phase refusal ⟦criterion 2⟧
- [ ] criterion-finished.sh accepts a ledger whose step prose quotes a criterion marker, with no more-than-one-criterion-tag refusal, and counts that step only toward the criterion of its trailing marker run ⟦criterion 2⟧

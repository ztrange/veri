# Plan for #934 — metrics.sh counts a ticked ⟦full-suite⟧ line as not done, and prints unknown budget cells for refactor-kind steps

- [x] An event log with step-done marks for four cycle steps and none for a fifth full-suite step, beside a ledger with all five lines ticked, reports "Steps done: 5 of 5 planned." ⟦criterion 1⟧
- [x] The same log beside a ledger whose full-suite line is unticked, as after a red full-suite run, reports "Steps done: 4 of 5 planned." ⟦criterion 2⟧
- [x] A run with no ledger beside its log still reports unknown for the planned figure ⟦criterion 2⟧
- [x] A By-step row whose only leaf phases are cover, transform and diff, with no revise or refactor mark, prints no unknown in its revise, refactor and stopped cells ⟦criterion 3⟧
- [x] A By-step row whose leaf phases are red, green and refactor, with no revise or refactor mark, still prints unknown in its revise, refactor and stopped cells ⟦criterion 4⟧

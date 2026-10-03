# Plan for #726 — the structural pass goes unmarked when no refactor-owed file exists, and its stopped= reason is unchecked

- [x] event.sh refuses a structural-pass mark whose stopped= is not candidates-done, budget-spent or nothing-structural with exit 2, naming the value and the three allowed ones on stderr, and appends nothing to the event log ⟦criterion 1⟧
- [x] event.sh refuses a structural-pass mark carrying no stopped= argument with exit 2, naming the three allowed reasons, and appends nothing to the event log ⟦added⟧ ⟦criterion 1⟧
- [x] event.sh refuses a structural-pass mark with stopped=budget-spent whose transforms is not equal to its budget with exit 2, and appends nothing to the event log ⟦criterion 2⟧
- [x] SKILL.md's structural-pass step says a missing .tdd/issue-<n>-refactor-owed.md is the refactor-owed.sh list exit-3 case, marked stopped=nothing-structural before the PR is readied ⟦criterion 3⟧ ⟂ refactor pending
- [ ] metrics.sh on a log that reaches a draft PR (a done mark) but carries no structural-pass mark renders the #### Structural pass section with a row saying the pass was not marked ⟦criterion 4⟧

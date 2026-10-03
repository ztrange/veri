### event.sh refuses a structural-pass mark whose stopped= is not candidates-done, budget-spent or nothing-structural with exit 2, naming the value and the three allowed ones on stderr, and appends nothing to the event log ⟦criterion 1⟧
- test-only | event.test.sh's #726 case never runs `rm -rf "$sp_work"`, but the cases before it clean up their scratch dirs (for example `rm -rf "$rs_work"`).
### event.sh refuses a structural-pass mark carrying no stopped= argument with exit 2, naming the three allowed reasons, and appends nothing to the event log ⟦added⟧ ⟦criterion 1⟧
- event.sh's case pattern `candidates-done|budget-spent|nothing-structural` repeats the reasons that `$stopped_reasons` now lists for the messages; one could be derived from the other, but that costs more code than it saves
- test-only | fold event.test.sh's two #726 cases into one loop over (args, expected words), since they differ only in the stopped= argument and the words stderr must name
- test-only | remove the scratch dirs `$sp_work` and `$ns_work` with `rm -rf` at the end of event.test.sh's two #726 cases, as the cases before them do
### event.sh refuses a structural-pass mark with stopped=budget-spent whose transforms is not equal to its budget with exit 2, and appends nothing to the event log ⟦criterion 2⟧
- test-only | event.test.sh's three #726 cases repeat the same scratch-dir / run event.sh / assert exit 2 / assert empty events.jsonl block and could share one helper
### metrics.sh on a log that reaches a draft PR (a done mark) but carries no structural-pass mark renders the #### Structural pass section with a row saying the pass was not marked ⟦criterion 4⟧
- test-only | the #726 case in metrics.test.sh repeats structural_mark_section's log-and-render sequence and its section-not-found check; a helper taking an optional mark could absorb both

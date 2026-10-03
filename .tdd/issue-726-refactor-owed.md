### event.sh refuses a structural-pass mark whose stopped= is not candidates-done, budget-spent or nothing-structural with exit 2, naming the value and the three allowed ones on stderr, and appends nothing to the event log ⟦criterion 1⟧
- test-only | event.test.sh's #726 case never runs `rm -rf "$sp_work"`, but the cases before it clean up their scratch dirs (for example `rm -rf "$rs_work"`).
### event.sh refuses a structural-pass mark carrying no stopped= argument with exit 2, naming the three allowed reasons, and appends nothing to the event log ⟦added⟧ ⟦criterion 1⟧
- event.sh's case pattern `candidates-done|budget-spent|nothing-structural` repeats the reasons that `$stopped_reasons` now lists for the messages; one could be derived from the other, but that costs more code than it saves
- test-only | fold event.test.sh's two #726 cases into one loop over (args, expected words), since they differ only in the stopped= argument and the words stderr must name
- test-only | remove the scratch dirs `$sp_work` and `$ns_work` with `rm -rf` at the end of event.test.sh's two #726 cases, as the cases before them do

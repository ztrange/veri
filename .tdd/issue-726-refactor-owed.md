### event.sh refuses a structural-pass mark whose stopped= is not candidates-done, budget-spent or nothing-structural with exit 2, naming the value and the three allowed ones on stderr, and appends nothing to the event log ⟦criterion 1⟧
- test-only | event.test.sh's #726 case never runs `rm -rf "$sp_work"`, but the cases before it clean up their scratch dirs (for example `rm -rf "$rs_work"`).

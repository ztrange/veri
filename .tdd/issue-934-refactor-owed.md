### The same log beside a ledger whose full-suite line is unticked, as after a red full-suite run, reports "Steps done: 4 of 5 planned." ⟦criterion 2⟧
- test-only | extract the shared four-step log + ledger setup of test_issue_934_a_ticked_full_suite_line_with_no_step_done_mark_counts_as_done and test_issue_934_an_unticked_full_suite_line_does_not_count_as_done into one helper parameterised by the full-suite checkbox
### A By-step row whose only leaf phases are cover, transform and diff, with no revise or refactor mark, prints no unknown in its revise, refactor and stopped cells ⟦criterion 3⟧
- test-only | extract the four-line cover/transform/diff event setup shared by the two new issue-934 budget-cell tests in test_metrics.py into one helper

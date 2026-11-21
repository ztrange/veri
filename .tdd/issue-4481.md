# Plan for #4481 — step-close and step-tick stop before the step-done mark when the step's criterion is already ticked, so metrics undercount steps

- [ ] step-close.sh, when tick-issue-criterion.sh exits 3 for a finished criterion of the step (the criterion is already ticked), writes the event.sh step-done mark and exits 0 with its usual next= line, in-process with the close fixture of tests/py/unit/test_step_close.py (small case) ⟦criterion 1⟧
- [ ] step-close.sh, when tick-issue-criterion.sh exits 1, stops at 6 before the step-done mark and exits 1, writing no event.sh step-done call, in-process with the close fixture (small case) ⟦criterion 3⟧
- [ ] step-close.sh, when tick-issue-criterion.sh exits 2, stops at 6 before the step-done mark and exits 2, writing no event.sh step-done call, in-process with the close fixture (small case) ⟦criterion 3⟧
- [ ] step-tick.sh, closing a ⟦diff-checked⟧ step whose criterion is already ticked (tick-issue-criterion.sh exits 3), writes the event.sh step-done mark and exits 0 with its next= line, in-process with the tick fixture of tests/py/unit/test_step_tick.py (small case) ⟦criterion 2⟧
- [ ] metrics.sh <n>, on a journal where a step's criterion was already ticked (a criterion-unticked event for the step followed by its step-done mark), counts that step in Steps done, in-process (small case) ⟦criterion 4⟧

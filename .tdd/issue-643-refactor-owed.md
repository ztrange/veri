### metrics.sh, given an event log whose awake clock advanced one second further than its wall clock over the issue span, prints `0 s` on the not-running line, never a negative number ⟦criterion 1⟧
- fold the two near-identical #643 fixture blocks (level_clocks / ahead_clocks: three `sv` lines each, differing only in the final awake reading and PR number) into one fixture helper

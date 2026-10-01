# Plan for #643 — metrics.sh reports -1 s not running when the awake and wall clocks round apart

- [x] metrics.sh, given an event log whose awake clock advanced exactly as far as its wall clock over the issue span, prints `0 s` on the not-running line ⟦criterion 1⟧
- [x] metrics.sh, given an event log whose awake clock advanced one second further than its wall clock over the issue span, prints `0 s` on the not-running line, never a negative number ⟦criterion 1⟧ ⟂ refactor pending
- [ ] metrics.sh, given an event log whose awake clock advanced one second further than its wall clock over the issue span, prints an issue wall time no larger than the wall-clock span ⟦criterion 2⟧
- [ ] metrics.sh, given an event log with a real suspend (awake clock behind the wall clock by many seconds), still prints that suspend's seconds on the not-running line and the awake span as the issue wall time ⟦criterion 3⟧

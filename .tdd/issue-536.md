# Plan for #536 — bg_start replaces the caller's EXIT trap instead of chaining onto it

- [x] A shell that set an EXIT trap before calling `bg_start` still runs that earlier trap at exit, and still gets the survivor report for a process left running ⟦criterion 1⟧
- [ ] A shell that set an EXIT trap and then calls `bg_start` more than once, with the same record and with a second record, reports each survivor exactly once and runs its own earlier trap exactly once ⟦criterion 2⟧
- [ ] Running `workqueue.test.sh` leaves no scratch directory of its own behind in `$TMPDIR` ⟦criterion 3⟧

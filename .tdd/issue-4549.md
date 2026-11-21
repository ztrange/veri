# Plan for #4549 — pin-reject-route.sh exits 2 on the bare TARGET_TEST case name PIN.md tells the conductor to pass

- [x] given a bare case name and a `.tdd/develop-red.out` beside the ledger whose `TEST_PATH` file holds that name, pin-reject-route runs the case in that file instead of exiting 2 ⟦criterion 1⟧
- [ ] given a bare case name the step's `TEST_PATH` file does not hold, pin-reject-route still exits 2 and ticks nothing ⟦criterion 2⟧

# Plan for #4511 — diff-step.sh rechecks a re-pin step's pin from the re-pin plan commit, so the range leaves out the disarming fix and pin-recheck exits 3

- [ ] on a re-pin step, diff-step.sh runs pin-recheck.sh from the `<green>~1` of the step whose pin it re-arms, so a pin left green under its mutation is a verify-diff REJECT, not a tick ⟦criterion 1⟧

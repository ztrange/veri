### A failing fast command printing more than 128 KB with no line containing ` FAIL `, whose final line carries a unique marker, leaves a non-empty `.tdd/verify-pin.reason` that includes that final line (the last lines of the output, a bounded tail) ⟦criterion 1⟧
- test-only | share the stub-building boilerplate between the new 2909 cases
### A failing fast command printing far more than 128 KB in which every line (or many lines) contains ` FAIL ` leaves a `.tdd/verify-pin.reason` whose size is under a stated cap named in pin_fast_tier.py: the ` FAIL ` blocks are kept only up to a cap, followed by the bounded tail ⟦criterion 2⟧
- test-only | fold the repeated shell-loop stub builders (20000-line generators) in test_pin_fast_tier_process.py into one helper

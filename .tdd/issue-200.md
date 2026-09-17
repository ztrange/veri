# Plan for #200 — A preflight baseline can fail under concurrent runs, so a run bails claiming main is red when it is green

- [x] The recovered attempt in `supervise-retry.test.sh` passes when the machine is loaded: a test runs it beside N busy-loop processes and asserts `1 passed`
- [x] The suite's heartbeat window leaves at least 5 s of margin over the recovered attempt's first output, without lengthening `make test` by more than that
- [x] Any other suite under `make test` with the same collision shape (a 1 s heartbeat window a loaded CPU can miss, e.g. `supervise.test.sh`, `verify.test.sh`) is fixed alongside, or named as checked and clear
- [ ] The late-start check in `hermetic-suites.test.sh` (a leaf started 3 s late under a window short of 6 s) runs only the `supervise.test.sh` and `verify.test.sh` cases whose widened windows it protects, not a full second pass of either suite, so `make test` stays inside CI's `timeout-minutes: 3`

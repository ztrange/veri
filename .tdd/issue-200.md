# Plan for #200 — A preflight baseline can fail under concurrent runs, so a run bails claiming main is red when it is green

- [x] The recovered attempt in `supervise-retry.test.sh` passes when the machine is loaded: a test runs it beside N busy-loop processes and asserts `1 passed`
- [ ] The suite's heartbeat window leaves at least 5 s of margin over the recovered attempt's first output, without lengthening `make test` by more than that
- [ ] Any other suite under `make test` with the same collision shape (a 1 s heartbeat window a loaded CPU can miss, e.g. `supervise.test.sh`, `verify.test.sh`) is fixed alongside, or named as checked and clear

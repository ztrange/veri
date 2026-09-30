# Plan for #563 — supervise's awake clock is always 0 under Apple's python3 3.9, so stuck leaves are never killed

- [x] supervise.sh's awake clock advances across separate processes under a python3 whose time.monotonic() restarts per process: with a stub python3 on PATH mimicking that, the hard timeout and the heartbeat kill still fire ⟦criterion 1⟧
- [ ] event.sh's awake reading (which metrics.sh subtracts across processes) comes from the same system-wide clock as supervise.sh, so it advances across processes under that stub python3 ⟦criterion 3⟧
- [ ] supervise-retry.test.sh and verify.test.sh pass with /usr/bin/python3 first on PATH on macOS ⟦full-suite⟧ ⟦criterion 2⟧
- [ ] CI (Linux) stays green: the full suite passes ⟦full-suite⟧ ⟦criterion 4⟧

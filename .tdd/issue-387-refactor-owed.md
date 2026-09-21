### an unknown --mode value, both an issue and --all, neither, and a non-integer issue each exit 2, write no .tdd/stop and signal nothing
- extract the shared mode vocabulary `at-ledger|at-leaf|now` from stop-run.sh and stop-requested.sh into a sourced lib helper
### an issue with no worktree, an issue whose .tdd/conductor.pid names no live process, and --all with no live run each exit 3 and write no .tdd/stop
- narrow the out/code/err globals that leak between cases — case 7's three sub-checks read whatever the previous one left, so a sub-check whose command never ran passes on stale values (verified with a probe: mistyping the third call to run_stop_in still reported 7 passed)

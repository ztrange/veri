### an unknown --mode value, both an issue and --all, neither, and a non-integer issue each exit 2, write no .tdd/stop and signal nothing
- extract the shared mode vocabulary `at-ledger|at-leaf|now` from stop-run.sh and stop-requested.sh into a sourced lib helper
### an issue with no worktree, an issue whose .tdd/conductor.pid names no live process, and --all with no live run each exit 3 and write no .tdd/stop
- narrow the out/code/err globals that leak between cases — case 7's three sub-checks read whatever the previous one left, so a sub-check whose command never ran passes on stale values (verified with a probe: mistyping the third call to run_stop_in still reported 7 passed)
### stop-run.sh --mode now <n> sends TERM to the pid in <run>/.tdd/<name>.pid whose process runs `supervise.sh <name> `, and to no pid whose process is gone or runs something else
- stop_leaves()'s `[[ -f "$pidfile" ]] || continue` is now dead — pid_in() returns 1 for the unmatched-glob literal too, so the guard can go
- the three fixture helpers hand their pid back through a global the caller copies on the next line (`sup_pid="$supervisor_pid"`, `green_sup="$supervisor_pid"`, `run_conductor_pid="$conductor_pid"`); a helper taking the name to set would drop the copy

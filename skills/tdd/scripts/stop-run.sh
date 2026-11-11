#!/bin/sh
# stop-run.sh — the operator's stop command: ask a run to stop, where its conductor looks. A shim over veri/stop_run.py.
#
# Runs are found under the main working tree of the caller's repository; `--mode` says when the
# stop takes effect: `at-ledger` (the default), `at-leaf` or `now`.
#
# `--mode now` also signals a detached command (a `.tdd/<name>.pid` session leader that is not a
# supervisor, only while the pid still runs the command veri recorded): TERM to its whole process
# group, then KILL after `VERI_STOP_KILL_GRACE` (default 5 seconds). A `.tdd/<name>.pid` is
# signalled, supervisor or detached command, only when its line 2 holds the start time of the
# process now at that pid; a file with no line 2 (written by an older skill snapshot) is left
# alone with one stderr line naming it, and a different start time (a reused pid) silently.
#
# usage: stop-run.sh [--mode <mode>] <issue> | --all
# Exits:   0 the stopped runs printed | 2 arguments that name no run, no mode this script
#          knows, typed from the skill's own scripts directory, or a main working tree that does not
#          hold the directory it was typed from, a group member that survives the KILL, a KILL
#          refused (`PermissionError`) or a refused survivor probe, each naming the pid and the run
#          on stderr (under `--all` any one run exiting 2 makes the call exit 2, every other run
#          still stopped) | 3 nothing to do — no live
#          run answered to what was named
export VERI_CALLER_DIR="$PWD"
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stop_run.py" "$@"

#!/bin/sh
# stop-run.sh — the operator's stop command: ask a run to stop, where its conductor looks. A shim over veri/stop_run.py.
#
# Runs are found under the main working tree of the caller's repository; `--mode` says when the
# stop takes effect: `at-ledger` (the default), `at-leaf` or `now`.
#
# usage: stop-run.sh [--mode <mode>] <issue> | --all
# Exits:   0 the stopped runs printed | 2 arguments that name no run, or no mode this script
#          knows | 3 nothing to do — no live run answered to what was named
exec python3 "$(dirname "$0")/veri/stop_run.py" "$@"

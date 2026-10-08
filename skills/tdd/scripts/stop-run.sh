#!/bin/sh
# stop-run.sh — the operator's stop command: ask a run to stop, where its conductor looks. A shim over veri/stop_run.py.
#
# Runs are found under the main working tree of the caller's repository; `--mode` says when the
# stop takes effect: `at-ledger` (the default), `at-leaf` or `now`.
#
# usage: stop-run.sh [--mode <mode>] <issue> | --all
# Exits:   0 the stopped runs printed | 2 arguments that name no run, no mode this script
#          knows, or typed from the skill's own scripts directory | 3 nothing to do — no live
#          run answered to what was named
export VERI_CALLER_DIR="$PWD"
exec python3 "$(dirname "$0")/veri/stop_run.py" "$@"

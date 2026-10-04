#!/bin/sh
# ensure-run-state-ignored.sh — install veri's run-state rule into a target repo's .gitignore and info/exclude: a shim over veri/ensure_run_state_ignored.py.
#
# usage: ensure-run-state-ignored.sh [repo-root]      (default: the current directory)
# Exit:    0 added or already present; 1 a write that failed; 2 a refusal, or a root git cannot resolve
exec python3 "$(dirname "$0")/veri/ensure_run_state_ignored.py" "$@"

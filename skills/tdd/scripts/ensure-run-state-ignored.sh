#!/bin/sh
# ensure-run-state-ignored.sh — install veri's run-state rule into a target repo's .gitignore and info/exclude: a shim over veri/ensure_run_state_ignored.py.
#
# usage: ensure-run-state-ignored.sh [repo-root]      (default: the current directory)
# Exit:    0 added or already present; 2 a refusal, a write to .gitignore or info/exclude that failed, or a root git cannot resolve
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/ensure_run_state_ignored.py" "$@"

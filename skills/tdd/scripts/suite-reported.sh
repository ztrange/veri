#!/bin/sh
# suite-reported.sh — say whether a developer leaf left its `SUITE:` report: a shim over veri/suite_reported.py.
#
# usage: suite-reported.sh <leaf-name>      (run from the worktree; reads .tdd/<leaf-name>.out)
# Exit:  0 a `SUITE:` line; 2 no `SUITE:` line (appends a report-missing event), or bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/suite_reported.py" "$@"

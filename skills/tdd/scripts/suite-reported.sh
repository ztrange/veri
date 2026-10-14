#!/bin/sh
# suite-reported.sh — say whether a developer leaf left its `SUITE:` report: a shim over veri/suite_reported.py.
#
# usage: suite-reported.sh <leaf-name>      (run from the worktree; reads .tdd/<leaf-name>.out)
# Exit:  2 no `SUITE:` line, or bad arguments
exec python3 "$(dirname "$0")/veri/suite_reported.py" "$@"

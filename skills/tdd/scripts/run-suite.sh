#!/bin/sh
# run-suite.sh — run ONE suite and hold it to the count-line contract the `test` recipe holds every suite to: a shim over veri/run_suite.py.
#
# usage: run-suite.sh <suite>
# Exit:    the suite's own code once its last line is `<n> passed, <m> failed`; 1 a suite with no count
#          line, or a failing pytest case; 2 a missing argument, an unreadable guard, pytest not importable,
#          or a terminated run
exec python3 "$(dirname "$0")/veri/run_suite.py" "$@"

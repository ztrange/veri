#!/bin/sh
# suite-red-resume.sh — decide whether a resumed run's red baseline may go on: a shim over veri/suite_red_resume.py.
#
# usage: suite-red-resume.sh check <ledger-file> <branch-red-file> <default-red-file>
#        suite-red-resume.sh insert <ledger-file> <branch-red-file>
# Exit:    0 the last bail was suite-red and no branch-red suite is red on the default branch — the branch-red file is printed;
#          1 the last bail was not suite-red or there is none, or a branch-red suite is also red on the default branch (named on stderr);
#          2 bad arguments, or a file could not be read
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/suite_red_resume.py" "$@"

#!/bin/sh
# detect-test-command.sh — print the command of the tier asked for (default: the full suite) of a repo: a shim over veri/detect_test_command.py.
#
# Precedence is first-match-wins: for --tier all only, the issue's `Test command:` line (never for
# --tier fast); then the tier markers in the repo's CLAUDE.md, then .veri/test-command, then
# inference from the repo's files.
#
# usage:   detect-test-command.sh [--tier fast|all] [--issue <body-file>] [repo-root]
#          (repo-root defaults to the current directory)
# Exit:    0 a command printed on stdout; 1 --tier or --issue with no value; 3 cannot decide, nothing printed
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/detect_test_command.py" "$@"

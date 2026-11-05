#!/bin/sh
# detect-test-command.sh — print the command of the tier asked for (default: the full suite) of a repo: a shim over veri/detect_test_command.py.
#
# Precedence is first-match-wins: for --tier all (the default) only (never for --tier fast or "one test file"), the issue's `Test command:` line (never for
# --tier fast; dropped when it equals the fast tier's command or is CLAUDE.md's `veri: all tests:`
# command plus a ` TESTS=` selector); then the tier markers in the repo's CLAUDE.md, then .veri/test-command, then
# inference from the repo's files.
#
# usage:   detect-test-command.sh [--tier fast|all|"one test file"] [--issue <body-file>] [repo-root]
#          (repo-root defaults to the current directory)
# Exit:    0 a command printed on stdout; 2 --tier or --issue with no value; 3 cannot decide, nothing printed (for "one test file": no CLAUDE.md line)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/detect_test_command.py" "$@"

#!/bin/sh
# detect-test-command.sh — print the command of the tier asked for (default: the full suite) of a repo: a shim over veri/detect_test_command.py.
#
# Precedence is first-match-wins: for --tier all (the default) only (never for --tier fast, "one test file", "quiet test files" or lint), the issue's `Test command:` line (never for
# --tier fast; dropped when it equals the fast tier's command or is CLAUDE.md's `veri: all tests:`
# command plus a ` TESTS=` selector); then the tier markers in the repo's CLAUDE.md (`veri: <tier> tests:`, which
# /vinstall records; `veri: one test file:` and `veri: lint:` for those two tiers, which nothing else answers;
# `veri: quiet test files:`), then inference from the repo's files (for "quiet test files" only a pytest
# configuration, giving `pytest -q --no-header -rf`, or a jest package.json test script, giving `npx jest --silent`).
#
# With --at <commit>, every repo file is read as <commit> holds it (CLAUDE.md and each file inference reads), never from
# repo-root's working tree: what preflight reads the fast command at, the branch base (#4263).
#
# usage:   detect-test-command.sh [--tier fast|all|"one test file"|"quiet test files"|lint] [--issue <body-file>] [--at <commit>] [repo-root]
#          (repo-root defaults to the current directory)
# Exit:    0 a command printed on stdout; 2 --tier, --issue or --at with no value, or an --at naming no commit git resolves in repo-root; 3 cannot decide, nothing printed (for "one test file" or lint: no CLAUDE.md line; for "quiet test files": no line and no runner recognised)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/detect_test_command.py" "$@"

#!/bin/sh
# record-test-commands.sh — commit a project's test commands to its CLAUDE.md and open a PR: a shim over veri/record_test_commands.py.
#
# Cuts the branch veri-install from the default branch's tip as origin holds it, one commit changing only the root
# CLAUDE.md (its `veri: fast tests:` and `veri: all tests:` lines, and with --one-file its `veri: one test file:`
# line, replaced where they stand, else appended), pushes it and opens a pull request against the default branch.
# Never merges; the checkout it runs from is left as it was.
#
# Usage:   record-test-commands.sh [--one-file <cmd>] <fast-cmd> <all-cmd> [repo-root]   (repo-root: default the current directory)
# Exit:    0 the PR's URL printed; 2 a missing or empty command, not a git repository, origin already has veri-install,
#          or no answer from git or gh; 3 the default branch's tip already declares every given command exactly
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/record_test_commands.py" "$@"

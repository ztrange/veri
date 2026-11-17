#!/bin/sh
# record-test-commands.sh — commit a project's test commands to its CLAUDE.md and open a PR: a shim over veri/record_test_commands.py.
#
# Cuts the branch veri-install from the default branch's tip as origin holds it, one commit changing only the root
# CLAUDE.md (its `veri: fast tests:` and `veri: all tests:` lines, and with --one-file its `veri: one test file:`
# line, replaced where they stand, else appended), pushes it and opens a pull request against the default branch.
# Never merges; the checkout it runs from is left as it was.
#
# Usage:   record-test-commands.sh [--one-file <cmd>] <fast-cmd> <all-cmd> [repo-root]   (repo-root: default the current directory)
# Exit:    0 the PR's URL printed, also on a re-run that finds origin's veri-install at exactly the commit it would push
#          and no PR open from it; 2 a missing or empty command, a --one-file command without "$1" (or a $1 word), not a
#          git repository, a CLAUDE.md that is not a regular file or would not read back each command exactly, origin's
#          veri-install holding anything else (other commands, or cut from an older default tip), or no answer from
#          git or gh; 3 the default branch's tip already declares every given command exactly, or a PR from
#          veri-install at exactly that commit is already open
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/record_test_commands.py" "$@"

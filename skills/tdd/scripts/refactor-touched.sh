#!/bin/sh
# refactor-touched.sh — print the files a step's green commit touched, as the bounds of that
# step's refactor: a shim over veri/refactor_touched.py.
#
# The ledger under `.tdd/` is run state, not code a refactor may tidy, so it is left out.
#
# usage: refactor-touched.sh <commit> | --issue <base> [--candidate <text>]
#
# Prints the touched files comma-joined, in `git diff --name-only` order: those <commit>
# touched, or with `--issue` every file changed between <base> and HEAD.
# Exit:    0 files printed; 2 a missing or unresolvable <commit>/<base>; 3 nothing outside .tdd/ touched
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/refactor_touched.py" "$@"

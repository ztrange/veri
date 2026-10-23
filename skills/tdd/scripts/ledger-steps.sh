#!/bin/sh
# ledger-steps.sh — print the ledger_steps records for the ledger on stdin: a shim over veri/ledger_steps.py.
#
# usage: ledger-steps.sh [current|last-done|current-or-last-done|next-phase|criterion <k>|has-mark <name>]
#
#   (none)    every record
#   current   the first refactor-pending step's text, else the first open step's; exit 3 if neither
#   last-done the last done step's text; exit 3 if none
#   current-or-last-done current's answer, else last-done's; exit 3 if neither
#   next-phase the next unmarked phase of the first unfinished phased step; exit 3 if none
#   has-mark  exit 0 if a step's trailing markers carry ⟦<name>⟧; exit 3 if none does
#   criterion the k-th checkbox's text under `## Acceptance criteria`; exit 3 if fewer than k
# Exit:    0 an answer printed; 2 an unknown verb, or criterion without an integer <k>; 3 nothing qualifies
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/ledger_steps.py" "$@"

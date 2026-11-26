#!/bin/sh
# skill-edit-step.sh — apply the requirements an issue states to a unit's list: a shim over veri/skill_edit_step.py.
#
# Usage:   skill-edit-step.sh [--change "<change>"] [--added "<step>"] <issue-body-file> <unit-file> [<pin-file>...]
#          each pin file is a test file the author may change; it is committed with the unit, list and GRADED
#          --change runs an author even on a unit already graded PASS; the unit's prose or its REQUIREMENTS.md rows must differ afterwards, else exit 1
# Env:     VERI_SKILL_EDIT_BUDGET author attempts, a whole number >= 1 (default 3)
# Exit:    0 list and GRADED committed after an author attempt; 1 every attempt in the budget was rejected, by
#          the grader or by an UNTRACED sentence the verify-trace-rows leaf sent back to the author, or the leaf
#          answered UNTRACED for a row (a row-untraced bail, nothing committed);
#          2 bad arguments, budget or heading, or no answer, or a trace answer still not one line per claim
#          after the VERI_NO_VERDICT_RETRIES relaunches, or, before any author runs, a path changed since
#          HEAD beyond the unit, its list, GRADED, the pins, the ledger files and the issue-body file (each
#          printed on stderr; nothing launched, unit, list and GRADED unchanged); 3 nothing left to commit, without --change: the list
#          and GRADED were committed with no author run, or there was no list and none was stated
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/skill_edit_step.py" "$@"

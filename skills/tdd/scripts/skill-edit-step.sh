#!/bin/sh
# skill-edit-step.sh — apply the requirements an issue states to a unit's list: a shim over veri/skill_edit_step.py.
#
# Usage:   skill-edit-step.sh <issue-body-file> <unit-file>
# Env:     VERI_SKILL_EDIT_BUDGET author attempts, a whole number >= 1 (default 3)
# Exit:    0 list and GRADED committed after an author attempt; 1 the grader rejects every attempt;
#          2 bad arguments, budget or heading, or no answer; 3 no author needed, list and GRADED committed
exec python3 "$(dirname "$0")/veri/skill_edit_step.py" "$@"

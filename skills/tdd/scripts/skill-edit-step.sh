#!/bin/sh
# skill-edit-step.sh — apply the requirements an issue states to a unit's list: a shim over veri/skill_edit_step.py.
#
# Usage:   skill-edit-step.sh <issue-body-file> <unit-file>
# Env:     VERI_SKILL_EDIT_BUDGET author attempts, a whole number >= 1 (default 3)
# Exit:    3 changed IDs already pass, list and GRADED committed; 2 bad arguments or budget
exec python3 "$(dirname "$0")/veri/skill_edit_step.py" "$@"

#!/bin/sh
# skill-edit-step.sh — apply the requirements an issue states to a unit's list: a shim over veri/skill_edit_step.py.
#
# Usage:   skill-edit-step.sh <issue-body-file> <unit-file>
# Exit:    3 changed IDs already pass, list and GRADED committed; 2 bad arguments
exec python3 "$(dirname "$0")/veri/skill_edit_step.py" "$@"

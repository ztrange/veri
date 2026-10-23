#!/bin/sh
# skill-edit-guard.sh — check a skill-edit step touched only its unit and that unit's requirements: a shim over veri/skill_edit_guard.py.
#
# Usage:   skill-edit-guard.sh <unit-file> <base-sha>
# Exit:    0 only the unit and its REQUIREMENTS.md changed; 2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/skill_edit_guard.py" "$@"

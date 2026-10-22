#!/bin/sh
# skill-edit-guard.sh — check a skill-edit step touched only its unit and that unit's requirements: a shim over veri/skill_edit_guard.py.
#
# Usage:   skill-edit-guard.sh <unit-file> <base-sha>
# Exit:    0 only the unit and its REQUIREMENTS.md changed; 2 bad arguments
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/skill_edit_guard.py" "$@"

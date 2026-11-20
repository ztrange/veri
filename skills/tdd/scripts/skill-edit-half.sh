#!/bin/sh
# skill-edit-half.sh — a ⟦skill-edit⟧ step's clean path in one call: a shim over veri/skill_edit_half.py.
#
# Usage:   skill-edit-half.sh <n> [--change "<change>"]
# Exit:    2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/skill_edit_half.py" "$@"

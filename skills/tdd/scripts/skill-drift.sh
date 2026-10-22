#!/bin/sh
# skill-drift.sh — the bail report's block naming the conductor-path changes since the pinned skill commit: a shim over veri/skill_drift.py.
#
# Reads VERI_SKILL_COMMIT, VERI_SKILL_CLONE and VERI_SKILL_REF; takes no arguments.
#
# usage: skill-drift.sh
# Exit:  0 always
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/skill_drift.py" "$@"

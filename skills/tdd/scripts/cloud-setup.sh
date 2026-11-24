#!/bin/sh
# cloud-setup.sh — in a Claude Code cloud session, build veri's environment and put it on the session's PATH: a shim over veri/cloud_setup.py.
#
# Usage:   cloud-setup.sh
# Exit:    0 set up, or not a cloud session; 2 no answer
#
# No floor check: a cloud session's python3 is below VENV_FLOOR until this script runs, and veri/cloud_setup.py,
# written for Python 3.9, finds or installs the interpreter that meets it.
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/cloud_setup.py" "$@"

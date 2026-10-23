#!/bin/sh
# resume-clean.sh — discard what a killed leaf left uncommitted outside .tdd/: a shim over veri/resume_clean.py.
#
# Usage:   resume-clean.sh
# Exit:    0 cleaned; prints each discarded change as a git status short line
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/resume_clean.py" "$@"

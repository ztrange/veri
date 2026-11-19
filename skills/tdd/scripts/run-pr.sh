#!/bin/sh
# run-pr.sh — the Draft PR step's stages in one call, stopping at its seams (PRD 038.11): a shim over veri/run_pr.py.
#
# Usage:   run-pr.sh <n>
# Exit:    1 stopped at the title seam; 2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/run_pr.py" "$@"

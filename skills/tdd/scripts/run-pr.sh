#!/bin/sh
# run-pr.sh — the Draft PR step's stages in one call, stopping at its seams (PRD 038.11): a shim over veri/run_pr.py.
#
# Usage:   run-pr.sh <n> [--from <stage>] [--hand <stage>]...
# Exit:    0 after the body seam, no stage called; 1 a seam (title, body, stacked, hand) or a stage's 1;
#          2 bad arguments, a missing preflight or ledger, a stage's 2 or an exit outside 0-3; 3 a stage's 3, call again
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/run_pr.py" "$@"

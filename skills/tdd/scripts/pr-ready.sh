#!/bin/sh
# pr-ready.sh — mark draft PR <pr-number> ready for review once <sha> is its head, via gh_pr_ready: a shim over veri/pr_ready.py.
#
# With VERI_STATE_LABEL_ISSUE set, the ready PR's issue is labelled `pr-ready`; a refused label is named, the exit stays 0.
#
# usage: pr-ready.sh <pr-number> <sha>
# Exit:    0 marked ready; 2 bad arguments, or no answer from GitHub
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pr_ready.py" "$@"

#!/bin/sh
# pr-ready.sh — mark draft PR <pr-number> ready for review once <sha> is its head, via gh_pr_ready: a shim over veri/pr_ready.py.
#
# usage: pr-ready.sh <pr-number> <sha>
# Exit:    0 marked ready; 2 bad arguments, or no answer from GitHub
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pr_ready.py" "$@"

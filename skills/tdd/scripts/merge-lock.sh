#!/bin/sh
# merge-lock.sh — the merge lock: a shim over veri/merge_lock.py.
#
# Usage:   merge-lock.sh take | release | holder
# Exit:    0 success; 2 no answer — no verb, or an unknown one
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/merge_lock.py" "$@"

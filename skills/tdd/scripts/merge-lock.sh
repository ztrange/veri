#!/bin/sh
# merge-lock.sh — the merge lock: a shim over veri/merge_lock.py.
#
# Usage:   merge-lock.sh take | release | holder | gate --pid <pid> -- <cmd>
# Exit:    0 success; 1 release by a non-holder; 2 no answer — no verb, or an unknown one;
#          gate: <cmd>'s own code, no --pid or no command 2
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/merge_lock.py" "$@"

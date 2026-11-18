#!/bin/sh
# merge-lock.sh — the merge lock: a shim over veri/merge_lock.py.
#
# Usage:   merge-lock.sh take --pid <pid> [--owner <token>] | release --pid <pid> [--owner <token>] | release --force
#                     | holder | gate [--keep] --pid <pid> [--owner <token>] -- <cmd>
# Exit:    0 success; 1 release by a non-holder; 2 no answer — no verb, or an unknown one;
#          gate: <cmd>'s own code; 2 without running <cmd> when no --pid or no command, or the caller
#          (--pid, --owner) does not hold the lock: none held, or the holder record names another pid or owner
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/merge_lock.py" "$@"

#!/bin/sh
# pin-fast-tier.sh — run the fast tier over the tree a pin would commit: a shim over veri/pin_fast_tier.py.
#
# Usage: pin-fast-tier.sh <fast-cmd>   (run from the worktree; failing output goes to .tdd/verify-pin.reason)
# Exit:  0 the fast command passed; 1 it failed; 2 no command given
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pin_fast_tier.py" "$@"

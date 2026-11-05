#!/bin/sh
# full-tier-time.sh — read or record a full-tier command's elapsed seconds: a shim over veri/full_tier_time.py.
#
# usage: full-tier-time.sh [--record <seconds>] <command>
# Exit:    0 the recorded seconds printed; 2 bad arguments; 3 the command has no record
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/full_tier_time.py" "$@"

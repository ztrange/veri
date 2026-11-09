#!/bin/sh
# baseline-full-tier.sh — settle the preflight full-tier decision: a shim over veri/baseline_full_tier.py.
#
# usage: baseline-full-tier.sh <issue> <full-tier-command>
# Exit:    2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/baseline_full_tier.py" "$@"

#!/bin/sh
# baseline-full-tier.sh — settle the preflight full-tier decision: a shim over veri/baseline_full_tier.py.
#
# usage: baseline-full-tier.sh <issue> <full-tier-command>
#        baseline-full-tier.sh --green <issue> <tree> <fast-command> <full-command>         # prints skip or run
#        baseline-full-tier.sh --record-green <issue> <tree> <fast-command> <full-command>  # records a green baseline
# Exit:    2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/baseline_full_tier.py" "$@"

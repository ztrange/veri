#!/bin/sh
# pr-checks.sh — the Draft PR step's sub-step 1 checks after pr-prepare.sh (DRAFT-PR.md), in one call: a shim over
# veri/pr_checks.py.
#
# Usage:   pr-checks.sh <n>
# Exit:    0 every check clean; 1 a check stopped for the conductor's judgement, named on the `stopped at` line;
#          3 the lint's wait ran out, call it again; 2 bad arguments, a missing input, or an inner call with no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pr_checks.py" "$@"

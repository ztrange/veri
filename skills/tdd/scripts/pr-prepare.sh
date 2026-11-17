#!/bin/sh
# pr-prepare.sh — the Draft PR step's sub-step 1 up to the structural pass's skip (DRAFT-PR.md), in one call: a shim
# over veri/pr_prepare.py.
#
# Usage:   pr-prepare.sh <n>
# Exit:    0 every call clean; 3 a wait ran out, call it again; 2 bad arguments or a missing input;
#          otherwise the stopping call's own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pr_prepare.py" "$@"

#!/bin/sh
# verify-branch.sh — the Draft PR step's whole-branch verifier stage, run after pr-checks.sh: a shim over veri/verify_branch.py.
#
# Usage:   verify-branch.sh <n>
# Exit:    2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/verify_branch.py" "$@"

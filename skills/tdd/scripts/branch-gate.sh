#!/bin/sh
# branch-gate.sh — on entering the Draft PR step, whether CI stands in for the branch's full run and, under `local`,
# that run and its recorded time (DRAFT-PR.md's opening paragraphs), in one call: a shim over veri/branch_gate.py.
#
# Usage:   branch-gate.sh <n>
# Exit:    0 every call clean; 3 a wait ran out, call it again; 2 bad arguments, an unchecked step left or a missing
#          input; otherwise the stopping call's own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/branch_gate.py" "$@"

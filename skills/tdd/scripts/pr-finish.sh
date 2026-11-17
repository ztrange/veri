#!/bin/sh
# pr-finish.sh — DRAFT-PR.md sub-step 2's second block up to the refactor-owed render, on its clean path: the
# ⟦full-suite⟧ ticks CI proved, the done mark, the metrics and their commit, the push, the second CI wait and the
# render, in one call: a shim over veri/pr_finish.py.
#
# Usage:   pr-finish.sh <n>
# Exit:    0 every call clean; 3 a wait's slice ran out, call it again; 2 bad arguments, a missing input or no PR;
#          otherwise the stopping call's own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pr_finish.py" "$@"

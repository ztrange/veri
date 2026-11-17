#!/bin/sh
# run-done.sh — DRAFT-PR.md sub-step 4 on its clean path: the stop ask, the final done comment and the clearing of a
# reported stop request, in one call: a shim over veri/run_done.py. It never merges.
#
# Usage:   run-done.sh <n>
# Exit:    0 every call clean; 2 bad arguments or a missing input; otherwise the stopping call's own code when neither
#          0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/run_done.py" "$@"

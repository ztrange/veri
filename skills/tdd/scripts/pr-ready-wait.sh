#!/bin/sh
# pr-ready-wait.sh — DRAFT-PR.md sub-step 2's first block on its clean path: the PR url read, the ⟦full-suite⟧ ticks owed
# to CI, the done mark, the metrics and their commit, the push, pr-ready.sh and the first wait-ci.sh, in one call: a
# shim over veri/pr_ready_wait.py.
#
# Usage:   pr-ready-wait.sh <n>
# Exit:    0 CI green; 3 a wait's slice ran out, call it again; 2 bad arguments, a missing input or no PR; otherwise
#          the stopping call's own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pr_ready_wait.py" "$@"

#!/bin/sh
# diff-step.sh — a ⟦diff-checked⟧ step's clean path (DIFF-CHECKED.md) in one call, sliced like a fused half: a shim
# over veri/diff_step.py.
#
# Usage:   diff-step.sh <n>
# Exit:    0 the step ticked, step-tick.sh's next= line last; 1 a REJECT (verify-diff or the flip), the step's
#          .tdd/issue-<n>-diff-step-rejected-wait left for revise.sh <n> diff, or another designed stop;
#          2 bad arguments, a missing input, no open ⟦diff-checked⟧ step, or no answer; 3 a wait ran out, call it
#          again; otherwise the stopping call's own code
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/diff_step.py" "$@"

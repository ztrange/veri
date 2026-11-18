#!/bin/sh
# run-step.sh — a cycle step's stages in one call, stopping at seams (PRD 038.2): a shim over veri/run_step.py.
#
# Usage:   run-step.sh <n> [--from <stage>] [--hand <stage>]…
# Exit:    0 step-close.sh exited 0, its next= line printed last; 1 a stage's 1, or a designed stop (hand,
#          unmodelled, record, kind); 2 bad arguments, a missing input, or a stage's 2; 3 a stage's 3, call it again
#          (or no open step)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/run_step.py" "$@"

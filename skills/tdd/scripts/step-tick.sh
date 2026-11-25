#!/bin/sh
# step-tick.sh — the close of a step no cycle closes (DIFF-CHECKED.md's PASS bullet, GO-RED.md), in one call: a shim
# over veri/step_tick.py. A ⟦diff-checked⟧ tick commits under `chore: diff-checked — <summary> (#<n>)`, a ⟦go-red⟧
# one under `test: go-red — <summary> (#<n>)`.
#
# Usage:   step-tick.sh <n>
# Exit:    0 every call clean, its last line next=draft-pr or next=cycle; 2 bad arguments, a missing preflight file or
#          ledger, no open step, or an open step neither
#          ⟦diff-checked⟧ nor ⟦go-red⟧, before any commit; 1 a change outside .tdd/ (tree-check), before the tick; otherwise the stopping call's
#          own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/step_tick.py" "$@"

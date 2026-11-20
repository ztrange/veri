#!/bin/sh
# go-red-step.sh — a ⟦go-red⟧ step's one stage (GO-RED.md): mutation-probe.sh on the case the step names, into the
# run's mutation record, then step-tick.sh: a shim over veri/go_red_step.py.
#
# Usage:   go-red-step.sh <n>
# Exit:    0 the step ticked, step-tick.sh's next= line last; 1 the probe saw no red, nothing ticked; 2 bad
#          arguments, a missing input, no open ⟦go-red⟧ step, a step naming no probe, the probe's 2, or the named
#          file not restored; otherwise the stopping call's own code
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/go_red_step.py" "$@"

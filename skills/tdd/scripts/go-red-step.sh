#!/bin/sh
# go-red-step.sh — a ⟦go-red⟧ step's one stage (GO-RED.md): mutation-probe.sh on the case the step names, then the
# .tdd/go-red-probed receipt (probe line, HEAD sha), then step-tick.sh: a shim over veri/go_red_step.py.
#
# Usage:   go-red-step.sh <n>
# Exit:    0 the step ticked, step-tick.sh's next= line last; 1 the probe saw no red, or the probe's <old> text is
#          absent from the named file (nothing probed), nothing ticked; 2 bad
#          arguments, a missing input, no open ⟦go-red⟧ step, a step naming no probe, no `veri: one test file:`
#          command (detect-test-command.sh exit 3) or its exit 2, the probe's 2, the named
#          file not restored, HEAD's sha unreadable, or any step-tick.sh exit but 0
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/go_red_step.py" "$@"

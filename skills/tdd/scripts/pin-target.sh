#!/bin/sh
# pin-target.sh — name the step's own pinning case: a shim over veri/pin_target.py.
#
# usage: pin-target.sh <step-red-report> [<red-missing-report>…]
# Exit:    0 the target printed
#          2 a missing argument, an unreadable report, or a report with no TARGET_TEST: line
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pin_target.py" "$@"

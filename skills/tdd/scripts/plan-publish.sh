#!/bin/sh
# plan-publish.sh — SKILL.md step 2's fixed tail once the plan is written, in one call: a shim over veri/plan_publish.py.
#
# Usage:   plan-publish.sh <n> <title-file>
# Exit:    0 every call clean, verify-plan PASS; 3 the verdict-plan wait ran out, call it again; 2 bad arguments or a
#          missing input; otherwise the stopping call's own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/plan_publish.py" "$@"

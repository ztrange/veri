#!/bin/sh
# revise.sh — REVISE.md's revise loop for one phase a verifier rejected, sliced like a fused half: a shim over
# veri/revise.py.
#
# Usage:   revise.sh <n> <phase>   (phase: red, green or refactor)
# Exit:    0 a revised PASS, the phase stage's wait re-saved; 3 a wait ran out, call it again; 2 bad arguments, a
#          missing input or no answer; otherwise the stopping call's own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/revise.py" "$@"

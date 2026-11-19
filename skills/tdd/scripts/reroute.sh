#!/bin/sh
# reroute.sh — wrong-test-route.sh's answer for the open step through the rerouted red leaf, verify-red and the
# frozen-test re-record (SKILL.md *Green*), sliced like a fused half: a shim over veri/reroute.py.
#
# Usage:   reroute.sh <n> <report>   (report: .tdd/develop-green.out, .tdd/revise-green-<k>.out or .tdd/verify-green.reason)
# Exit:    0 the rerouted red verified and the frozen tests re-recorded, retry green; 1 a stop naming the answer the
#          conductor routes, `route=revise phase=<phase>` when the answer is a revise, or the record seam; 3 a wait
#          ran out, call it again; 2 bad arguments, a missing input or no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/reroute.py" "$@"

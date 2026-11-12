#!/bin/sh
# parse-adjudication.sh — read the adjudicate leaf's answer: a shim over veri/parse_adjudication.py.
#
# usage: parse-adjudication.sh <leaf-output>
# Exit: 0 answer printed; 2 no answer, bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/parse_adjudication.py" "$@"

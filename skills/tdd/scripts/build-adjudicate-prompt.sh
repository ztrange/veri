#!/bin/sh
# build-adjudicate-prompt.sh — assemble the adjudicate leaf's prompt: a shim over veri/build_adjudicate_prompt.py.
#
# usage: build-adjudicate-prompt.sh <n> <cause> <exit-code> <stderr-file> <command…>
# Exit: 0 prompt printed; 2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(cd "$(dirname "$0")" && pwd)/veri/build_adjudicate_prompt.py" "$@"

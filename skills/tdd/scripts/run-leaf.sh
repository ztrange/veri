#!/bin/sh
# run-leaf.sh — build and run one `claude -p` leaf, streaming its output to stdout: a shim over veri/run_leaf.py.
#
# usage: run-leaf.sh <prompt-file|-> [claude args...]
#
# Exit: the leaf's own status when it is 0-3, else 2; 2 for a missing prompt argument.
if [ -z "${PYTHONCOERCECLOCALE+set}" ]; then
  PYTHONCOERCECLOCALE=0 VERI_SHIM_SET_COERCE=1
  export PYTHONCOERCECLOCALE VERI_SHIM_SET_COERCE
fi
exec python3 "$(dirname "$0")/veri/run_leaf.py" "$@"

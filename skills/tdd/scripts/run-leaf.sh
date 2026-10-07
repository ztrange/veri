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
# hazard: a signal ignored on entry cannot be trapped, so only a default one fires its trap.
VERI_SHIM_DEFAULT_SIGNALS=
for sig in PIPE XFSZ; do
  trap 'VERI_SHIM_DEFAULT_SIGNALS="$VERI_SHIM_DEFAULT_SIGNALS $sig"' "$sig"
  kill -s "$sig" $$
  trap - "$sig"
done
export VERI_SHIM_DEFAULT_SIGNALS
exec python3 "$(dirname "$0")/veri/run_leaf.py" "$@"

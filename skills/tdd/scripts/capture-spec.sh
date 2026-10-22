#!/bin/sh
# capture-spec.sh — write the blind spec the verifier leaves read, to stdout: a shim over veri/capture_spec.py.
#
# usage: capture-spec.sh <issue-number>
# Exit:  0 the spec printed; 2 no issue number, or gh failed on both routes.
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/capture_spec.py" "$@"

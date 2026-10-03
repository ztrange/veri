#!/bin/sh
# capture-spec.sh — write the blind spec the verifier leaves read, to stdout: a shim over veri/capture_spec.py.
#
# usage: capture-spec.sh <issue-number>
# Exit:  0 the spec printed; 2 no issue number, or gh failed on both routes.
exec python3 "$(dirname "$0")/veri/capture_spec.py" "$@"

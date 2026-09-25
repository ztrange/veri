#!/bin/sh
# parse-verdict.sh — entry shim; the transform is py/parse_verdict.py (migration spike).
d=${0%/*}; [ "$d" = "$0" ] && d=.
exec python3 "$d/py/parse_verdict.py" "$@"

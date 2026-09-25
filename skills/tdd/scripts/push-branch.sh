#!/bin/sh
# push-branch.sh — entry shim; the logic is py/push_branch.py (migration spike).
d=${0%/*}; [ "$d" = "$0" ] && d=.
exec python3 "$d/py/push_branch.py" "$@"

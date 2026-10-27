#!/bin/sh
# stale-rows.sh — grade the marked units' requirement rows of an issue: a shim over veri/stale_rows.py.
#
# usage: stale-rows.sh <issue>
# Exit:  0 every marked row passes · 1 a marked row fails · 2 bad arguments · 3 nothing to do
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stale_rows.py" "$@"

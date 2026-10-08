#!/bin/sh
# detach-leaf.sh — launch a leaf into a session of its own and return at once: a shim over veri/detach_leaf.py.
#
# usage: detach-leaf.sh <cmd> [args…]
# Exit:    0 launched; 2 no <cmd>, or <cmd> could not be started (named on stderr)
exec python3 "$(dirname "$0")/veri/detach_leaf.py" "$@"

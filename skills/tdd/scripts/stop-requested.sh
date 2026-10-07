#!/bin/sh
# stop-requested.sh — has an operator asked this run to stop, and how? A shim over veri/stop_requested.py.
#
# Reads `.tdd/stop` relative to the working directory; its first line is the mode, printed on stdout.
#
# usage: stop-requested.sh [--clear]
# Exits:   0 a mode was printed, or the request was cleared | 2 malformed request, or an
#          argument this script does not take | 3 no stop request
exec python3 "$(dirname "$0")/veri/stop_requested.py" "$@"

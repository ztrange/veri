#!/bin/sh
# harvest-usage.sh — turn one finished leaf's closing accounting into a `usage` event: a shim over veri/harvest_usage.py.
#
# usage: harvest-usage.sh <leaf-name>
#        reads `.tdd/<leaf-name>.log` relative to the directory it is run in.
# Exit:  0 a usage event appended; 1 no log file; 2 a missing or refused leaf name, or no answer;
#        3 nothing to do — no closing result record in the log
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/harvest_usage.py" "$@"
